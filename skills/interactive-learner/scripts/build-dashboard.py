#!/usr/bin/env python3
"""Build a student dashboard HTML from .learner-progress.json.

Usage: uv run .agents/skills/interactive-learner/scripts/build-dashboard.py [--progress <path>] [--output <path>] [--open]

Reads progress data and generates a visual dashboard showing:
- Total XP with level/rank
- Learning streak
- Per-course progress with score history
- Achievement badges
"""

import argparse
import html
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
SHELL_PATH = SKILL_DIR / "assets" / "dashboard-shell.html"
DEFAULT_PROGRESS = Path.cwd() / ".learner-progress.json"

# ── XP level thresholds (imported from progress.py — single source of truth) ──
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("progress", SCRIPT_DIR / "progress.py")
_prog = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_prog)
LEVELS = [(xp, name, "") for xp, _lvl, name in _prog.LEVEL_THRESHOLDS]
# Assign icons per level
_LEVEL_ICONS = ["🌱", "🧭", "🔧", "🏗️", "🎯", "🎓", "🏆", "👑"]
LEVELS = [(xp, name, _LEVEL_ICONS[i] if i < len(_LEVEL_ICONS) else "⭐") for i, (xp, name, _) in enumerate(LEVELS)]


def get_level(xp):
    """Return (level_name, level_icon, next_threshold) for given XP."""
    current = LEVELS[0]
    next_threshold = LEVELS[1][0] if len(LEVELS) > 1 else None
    for i, (threshold, name, icon) in enumerate(LEVELS):
        if xp >= threshold:
            current = (name, icon)
            next_threshold = LEVELS[i + 1][0] if i + 1 < len(LEVELS) else None
        else:
            break
    return current[0], current[1], next_threshold


def build_stat_row(data):
    """Build the top stat cards: XP, Streak, Level."""
    total_xp = data.get("total_xp", 0)
    streak = data.get("streak_days", 0)
    level_name, level_icon, next_xp = get_level(total_xp)

    streak_label = f"{streak} day{'s' if streak != 1 else ''}"
    if streak == 0:
        streak_label = "Start today!"

    xp_progress = ""
    if next_xp:
        remaining = next_xp - total_xp
        xp_progress = f'<div style="font-size:11px;color:var(--text-dim);margin-top:2px">{remaining} XP to next level</div>'

    return f'''<div class="stat-row animate-in delay-1">
  <div class="stat-card">
    <div class="stat-icon">⚡</div>
    <div class="stat-value xp">{total_xp}</div>
    <div class="stat-label">Total XP</div>
    {xp_progress}
  </div>
  <div class="stat-card">
    <div class="stat-icon">🔥</div>
    <div class="stat-value streak">{streak_label}</div>
    <div class="stat-label">Streak</div>
  </div>
  <div class="stat-card">
    <div class="stat-icon">{level_icon}</div>
    <div class="stat-value level">{level_name}</div>
    <div class="stat-label">Level</div>
  </div>
</div>'''


def build_course_card(course_id, course_data, delay_idx):
    """Build a course progress card with score bars."""
    name = course_id.replace("-", " ").replace("_", " ").title()
    current = course_data.get("current_session", 0)
    total = course_data.get("total_sessions", 0)
    scores = course_data.get("scores", [])
    max_scores = course_data.get("max_scores", [])
    xp = course_data.get("xp", 0)
    started = course_data.get("started", "")

    # Progress percentage — handle unknown total gracefully
    completed = len(scores)  # number of sessions actually finished
    if total > 0:
        pct = min(round((current / total) * 100), 100)
        progress_text = f"Session {current} of {total} — {pct}% complete"
    elif completed > 0:
        progress_text = f"{completed} session{'s' if completed != 1 else ''} completed"
    else:
        progress_text = "Not started"

    # For progress bar, use what we know
    pct = min(round((current / total) * 100), 100) if total > 0 else 0

    # Score history bars
    score_bars = ""
    if scores:
        for i, (s, m) in enumerate(zip(scores, max_scores)):
            height = round((s / m) * 100) if m > 0 else 0
            perfect = "perfect" if s == m else ""
            score_bars += f'<div class="score-bar {perfect}" style="height:{max(height, 8)}%" title="Session {i+1}: {s}/{m}"><span class="score-bar-label">S{i+1}</span></div>\n'

    score_section = ""
    if score_bars:
        score_section = f'''<div style="margin-top:20px">
    <div style="font-size:12px;color:var(--text-dim);font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">Score History</div>
    <div class="score-bars">{score_bars}</div>
    <div style="height:20px"></div>
  </div>'''

    # Only show progress bar if we know the total
    progress_bar = ""
    if total > 0:
        progress_bar = f'<div class="progress-bar"><div class="progress-bar-fill" style="width:{pct}%"></div></div>'

    return f'''<div class="course-card animate-in delay-{delay_idx}">
  <div class="course-top">
    <div>
      <div class="course-name">{html.escape(name)}</div>
      <div class="course-meta">Started {started}</div>
    </div>
    <span class="course-xp">⚡ {xp} XP</span>
  </div>
  {progress_bar}
  <div class="progress-text">{progress_text}</div>
  {score_section}
</div>'''


def build_curriculum_section(course_id, course_data, delay_idx):
    """Build an expandable curriculum section showing all planned sessions."""
    curriculum = course_data.get("curriculum")
    if not curriculum:
        return ""

    current_session = course_data.get("current_session", 0)
    scores = course_data.get("scores", [])
    max_scores = course_data.get("max_scores", [])
    name = course_id.replace("-", " ").replace("_", " ").title()

    sessions_html = ""
    for sess in curriculum:
        num = sess.get("session_number", 0)
        title = html.escape(sess.get("title", f"Session {num}"))
        desc = html.escape(sess.get("description", ""))
        objectives = sess.get("objectives", [])
        concepts = sess.get("concepts", [])
        est = sess.get("estimated_minutes", 0)

        # Status: completed / current / upcoming
        if num <= current_session and num <= len(scores):
            status = "completed"
            icon = '<span class="cur-status-icon completed">&#10003;</span>'
            score_idx = num - 1
            if 0 <= score_idx < len(scores):
                s, m = scores[score_idx], max_scores[score_idx] if score_idx < len(max_scores) else 0
                score_html = f'<span class="cur-score">{s}/{m}</span>'
            else:
                score_html = ""
        elif num == current_session + 1:
            status = "current"
            icon = '<span class="cur-status-icon current">&#9654;</span>'
            score_html = ""
        else:
            status = "upcoming"
            icon = ""
            score_html = ""

        obj_list = "".join(
            f'<li>{html.escape(o)}</li>' for o in objectives
        )
        obj_html = f'<ul class="cur-objectives">{obj_list}</ul>' if obj_list else ""

        est_html = f'<span class="cur-est">{est} min</span>' if est else ""

        sessions_html += f'''<div class="cur-session {status}">
      <div class="cur-session-header">
        {icon}
        <span class="cur-session-num">Session {num}</span>
        <span class="cur-session-title">{title}</span>
        {score_html}
        {est_html}
      </div>
      <div class="cur-details">
        <p class="cur-desc">{desc}</p>
        {obj_html}
      </div>
    </div>\n'''

    return f'''<div class="curriculum-card animate-in delay-{delay_idx}">
  <h2>Curriculum &mdash; {html.escape(name)}</h2>
  <div class="cur-sessions">{sessions_html}</div>
</div>'''


def build_achievements(earned_items):
    """Build achievement badges grid.

    Supports both legacy achievement IDs (list[str]) and dynamic achievements
    (list[dict] with id/icon/name/description).
    """
    earned_items = earned_items or []
    has_dynamic = any(isinstance(item, dict) for item in earned_items)

    # Normalize all items into dicts.
    normalized = []
    seen = set()

    for item in earned_items:
        if isinstance(item, dict):
            aid = str(item.get("id") or item.get("name") or "").strip()
            if not aid or aid in seen:
                continue
            seen.add(aid)
            normalized.append({
                "id": aid,
                "icon": item.get("icon", "🏅"),
                "name": item.get("name", aid.replace("-", " ").replace("_", " ").title()),
                "desc": item.get("description", item.get("desc", "Achievement unlocked")),
            })
        elif isinstance(item, str):
            aid = item
            if aid in seen:
                continue
            seen.add(aid)
            normalized.append({
                "id": aid,
                "icon": "🏅",
                "name": aid.replace("-", " ").replace("_", " ").title(),
                "desc": "Achievement unlocked",
            })

    if not normalized:
        return '''<div class="achievements-card animate-in delay-5">
  <h2>Achievements</h2>
  <p class="empty-state">Complete lessons to unlock achievements unique to your course!</p>
</div>'''

    badges = ""
    for ach in normalized:
        badges += f'''<div class="badge earned">
      <span class="badge-icon">{ach["icon"]}</span>
      <span class="badge-name">{html.escape(ach["name"])}</span>
      <span class="badge-desc">{html.escape(ach["desc"])}</span>
    </div>\n'''

    return f'''<div class="achievements-card animate-in delay-5">
  <h2>Achievements ({len(normalized)})</h2>
  <div class="badge-grid">{badges}</div>
</div>'''


def build_dashboard(progress_path, output_path=None):
    """Main build function."""
    if not progress_path.exists():
        print(f"❌ No progress file found at {progress_path}")
        print("Run: uv run .agents/skills/interactive-learner/scripts/progress.py init <course> <name>")
        sys.exit(1)

    data = json.loads(progress_path.read_text())
    shell = SHELL_PATH.read_text()

    # Greeting
    name = data.get("name", "Learner")
    hour = datetime.now().hour
    if hour < 12:
        time_greeting = "Good morning"
    elif hour < 17:
        time_greeting = "Good afternoon"
    else:
        time_greeting = "Good evening"

    total_sessions = sum(c.get("current_session", 0) for c in data.get("courses", {}).values())
    subtitle = f"You've completed {total_sessions} session{'s' if total_sessions != 1 else ''} across {len(data.get('courses', {}))} course{'s' if len(data.get('courses', {})) != 1 else ''}."

    # Build sections
    stat_row = build_stat_row(data)

    courses_html = ""
    curriculum_html = ""
    delay = 2
    for cid, cdata in data.get("courses", {}).items():
        courses_html += build_course_card(cid, cdata, delay)
        delay += 1
        cur = build_curriculum_section(cid, cdata, delay)
        if cur:
            curriculum_html += cur
            delay += 1

    achievements_html = build_achievements(data.get("achievements", []))

    # Assemble
    result = shell.replace("{{GREETING}}", f"{time_greeting}, {html.escape(name)}")
    result = result.replace("{{SUBTITLE}}", subtitle)
    result = result.replace("{{STAT_ROW}}", stat_row)
    result = result.replace("{{COURSES}}", courses_html)
    result = result.replace("{{CURRICULUM}}", curriculum_html)
    result = result.replace("{{ACHIEVEMENTS}}", achievements_html)

    if not output_path:
        output_path = Path.cwd() / "dashboard.html"
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result)
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(description="Build student dashboard HTML")
    parser.add_argument("--progress", "-p", help="Path to .learner-progress.json",
                        default=str(DEFAULT_PROGRESS))
    parser.add_argument("--output", "-o", help="Output HTML file path")
    parser.add_argument("--open", action="store_true", help="Open in browser after building")
    args = parser.parse_args()

    progress_path = Path(args.progress)
    out = build_dashboard(progress_path, args.output)
    print(f"✅ Dashboard built: {out}")

    if args.open:
        import platform
        if platform.system() == "Darwin":
            subprocess.run(["open", out])
            print("📊 Opened dashboard in browser")
        elif platform.system() == "Linux":
            subprocess.run(["xdg-open", out])
            print("📊 Opened dashboard in browser")
        else:
            subprocess.run(["start", out], shell=True)
            print("📊 Opened dashboard in browser")


if __name__ == "__main__":
    main()
