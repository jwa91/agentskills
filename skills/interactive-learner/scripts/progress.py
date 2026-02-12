#!/usr/bin/env python3
"""
Student progress tracker with concept-level mastery and dynamic achievements.

Usage:
  uv run .agents/skills/interactive-learner/scripts/progress.py init <course> <name>          # Create new student profile
  uv run .agents/skills/interactive-learner/scripts/progress.py show                           # Show current progress
  uv run .agents/skills/interactive-learner/scripts/progress.py show --concepts                # Show concept mastery details
  uv run .agents/skills/interactive-learner/scripts/progress.py update <course> --session N --score S --max M [--concepts '{"concept": 0.8}']
  uv run .agents/skills/interactive-learner/scripts/progress.py streak                         # Check/update streak
  uv run .agents/skills/interactive-learner/scripts/progress.py xp                             # Show total XP
  uv run .agents/skills/interactive-learner/scripts/progress.py review <course>                # Show concepts due for review
  uv run .agents/skills/interactive-learner/scripts/progress.py achieve <course> <id> <icon> <name> <description>  # Grant dynamic achievement
  uv run .agents/skills/interactive-learner/scripts/progress.py mission <course> <description> # Log a pending mission
  uv run .agents/skills/interactive-learner/scripts/progress.py mission-complete <course> <idx> # Mark a mission complete
  uv run .agents/skills/interactive-learner/scripts/progress.py set-curriculum <course> <curriculum.json>  # Save curriculum
"""

import json
import sys
import os
import argparse
import math
from datetime import datetime, timedelta
from pathlib import Path

PROGRESS_FILE = Path.cwd() / ".learner-progress.json"

# --- FSRS-lite constants ---
# Simplified Free Spaced Repetition Scheduler
# Stability = how many days until recall probability drops to 90%
INITIAL_STABILITY = 1.0     # 1 day for new concepts
STABILITY_GROWTH = 2.5      # multiplier on success
STABILITY_DECAY = 0.5       # multiplier on failure
MIN_STABILITY = 0.5
MAX_STABILITY = 365.0
REVIEW_THRESHOLD = 0.7      # recall probability below this = due for review


def load():
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text())
    return None


def save(data):
    PROGRESS_FILE.write_text(json.dumps(data, indent=2))


def init_profile(name, course):
    data = load() or {
        "name": name,
        "created": datetime.now().isoformat(),
        "background": [],
        "total_xp": 0,
        "level": 1,
        "streak_days": 0,
        "last_session_date": None,
        "achievements": [],
        "courses": {},
        "concept_mastery": {}
    }
    if "concept_mastery" not in data:
        data["concept_mastery"] = {}
    if course not in data.get("courses", {}):
        data["courses"][course] = {
            "started": datetime.now().isoformat()[:10],
            "current_session": 0,
            "total_sessions": 0,
            "scores": [],
            "max_scores": [],
            "xp": 0,
            "concepts": [],
            "pending_missions": [],
            "completed_missions": [],
            "open_responses": [],
            "notes": ""
        }
    save(data)
    print(json.dumps(data, indent=2))


def show(show_concepts=False):
    data = load()
    if not data:
        print('{"error": "No progress file found. Run: progress.py init <course> <name>"}')
        return
    if show_concepts and "concept_mastery" in data:
        # Show concept mastery with review status
        concepts = data["concept_mastery"]
        now = datetime.now()
        review_status = {}
        for cid, cdata in concepts.items():
            last_review = datetime.fromisoformat(cdata["last_reviewed"])
            days_since = (now - last_review).total_seconds() / 86400
            stability = cdata["stability"]
            # Recall probability: e^(-days/stability)
            recall_prob = math.exp(-days_since / stability) if stability > 0 else 0
            review_status[cid] = {
                "mastery": cdata["mastery"],
                "stability_days": round(stability, 1),
                "recall_probability": round(recall_prob, 2),
                "needs_review": recall_prob < REVIEW_THRESHOLD,
                "last_reviewed": cdata["last_reviewed"][:10],
                "review_count": cdata["review_count"],
                "course": cdata.get("course", "unknown")
            }
        output = {
            "student": data["name"],
            "total_xp": data["total_xp"],
            "level": data.get("level", 1),
            "streak_days": data["streak_days"],
            "concept_count": len(concepts),
            "concepts_needing_review": sum(1 for c in review_status.values() if c["needs_review"]),
            "concepts": review_status
        }
        print(json.dumps(output, indent=2))
    else:
        print(json.dumps(data, indent=2))


def update_concept_mastery(data, course, concepts_dict):
    """Update per-concept mastery scores.
    concepts_dict: {"concept-id": score} where score is 0.0-1.0
    """
    if "concept_mastery" not in data:
        data["concept_mastery"] = {}

    now = datetime.now().isoformat()

    for concept_id, score in concepts_dict.items():
        if concept_id in data["concept_mastery"]:
            c = data["concept_mastery"][concept_id]
            # Update mastery with exponential moving average
            c["mastery"] = round(c["mastery"] * 0.3 + score * 0.7, 3)
            # Update FSRS stability
            if score >= 0.7:
                c["stability"] = min(c["stability"] * STABILITY_GROWTH, MAX_STABILITY)
            else:
                c["stability"] = max(c["stability"] * STABILITY_DECAY, MIN_STABILITY)
            c["last_reviewed"] = now
            c["review_count"] += 1
            c["history"].append({"date": now[:10], "score": score})
            # Keep last 20 data points
            if len(c["history"]) > 20:
                c["history"] = c["history"][-20:]
        else:
            data["concept_mastery"][concept_id] = {
                "mastery": score,
                "stability": INITIAL_STABILITY,
                "last_reviewed": now,
                "introduced_in": now[:10],
                "review_count": 1,
                "course": course,
                "history": [{"date": now[:10], "score": score}]
            }

    # Also update course-level concept list
    if course in data["courses"]:
        existing = set(data["courses"][course].get("concepts", []))
        existing.update(concepts_dict.keys())
        data["courses"][course]["concepts"] = sorted(existing)


def get_review_concepts(data, course=None):
    """Return concepts due for review based on FSRS recall probability."""
    if "concept_mastery" not in data:
        return []

    now = datetime.now()
    due = []

    for cid, cdata in data["concept_mastery"].items():
        if course and cdata.get("course") != course:
            continue
        last_review = datetime.fromisoformat(cdata["last_reviewed"])
        days_since = (now - last_review).total_seconds() / 86400
        stability = cdata["stability"]
        recall_prob = math.exp(-days_since / stability) if stability > 0 else 0

        if recall_prob < REVIEW_THRESHOLD:
            due.append({
                "concept": cid,
                "mastery": cdata["mastery"],
                "recall_probability": round(recall_prob, 2),
                "days_since_review": round(days_since, 1),
                "review_count": cdata["review_count"],
                "course": cdata.get("course", "unknown")
            })

    # Sort by recall probability (lowest first = most urgent)
    due.sort(key=lambda x: x["recall_probability"])
    return due


def calculate_level(total_xp):
    """Level thresholds — increasingly spaced."""
    thresholds = [
        (0, 1, "Beginner"),
        (100, 2, "Explorer"),
        (300, 3, "Practitioner"),
        (600, 4, "Builder"),
        (1200, 5, "Specialist"),
        (2500, 6, "Expert"),
        (5000, 7, "Master"),
        (10000, 8, "Grandmaster"),
    ]
    level = 1
    title = "Beginner"
    for threshold, lvl, name in thresholds:
        if total_xp >= threshold:
            level = lvl
            title = name
    return level, title


def update_session(course, session, score, max_score, concepts_json=None):
    data = load()
    if not data:
        print('{"error": "No profile"}')
        return

    c = data["courses"].get(course)
    if not c:
        print(f'{{"error": "Course {course} not found"}}')
        return

    c["current_session"] = session
    c["scores"].append(score)
    c["max_scores"].append(max_score)

    # XP: 10 per correct + 25 bonus for perfect
    xp_earned = score * 10
    if score == max_score:
        xp_earned += 25
    c["xp"] += xp_earned
    data["total_xp"] += xp_earned

    # Update level
    level, title = calculate_level(data["total_xp"])
    old_level = data.get("level", 1)
    data["level"] = level

    # Update concept mastery if provided
    if concepts_json:
        try:
            concepts_dict = json.loads(concepts_json) if isinstance(concepts_json, str) else concepts_json
            update_concept_mastery(data, course, concepts_dict)
        except (json.JSONDecodeError, TypeError):
            pass  # Silently skip malformed concept data

    # Streak
    today = datetime.now().strftime("%Y-%m-%d")
    last = data.get("last_session_date")
    if last:
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        if last == yesterday:
            data["streak_days"] += 1
        elif last != today:
            data["streak_days"] = 1
    else:
        data["streak_days"] = 1
    data["last_session_date"] = today

    save(data)

    result = {
        "xp_earned": xp_earned,
        "total_xp": data["total_xp"],
        "level": level,
        "level_title": title,
        "leveled_up": level > old_level,
        "streak_days": data["streak_days"],
        "score": f"{score}/{max_score}",
        "session": session,
        "achievements": data.get("achievements", []),
        "concepts_tracked": len(data.get("concept_mastery", {}))
    }
    print(json.dumps(result, indent=2))


def grant_achievement(course, ach_id, icon, name, description):
    """Grant a dynamic achievement. Achievements are NOT hardcoded — the agent generates them
    based on the specific course, topic, and student milestones."""
    data = load()
    if not data:
        print('{"error": "No profile"}')
        return

    # Check if already earned
    for a in data.get("achievements", []):
        if a["id"] == ach_id:
            print(json.dumps({"already_earned": True, "achievement": a}))
            return

    achievement = {
        "id": ach_id,
        "icon": icon,
        "name": name,
        "description": description,
        "course": course,
        "earned_date": datetime.now().isoformat()[:10]
    }
    data.setdefault("achievements", []).append(achievement)
    save(data)
    print(json.dumps({"granted": True, "achievement": achievement}))


def add_mission(course, description):
    """Log a pending real-world mission."""
    data = load()
    if not data:
        print('{"error": "No profile"}')
        return
    c = data["courses"].get(course)
    if not c:
        print(f'{{"error": "Course {course} not found"}}')
        return

    c.setdefault("pending_missions", []).append({
        "description": description,
        "assigned_date": datetime.now().isoformat()[:10],
        "completed": False
    })
    save(data)
    print(json.dumps({"logged": True, "pending_missions": c["pending_missions"]}))


def complete_mission(course, idx):
    """Mark a mission as complete."""
    data = load()
    if not data:
        print('{"error": "No profile"}')
        return
    c = data["courses"].get(course)
    if not c:
        print(f'{{"error": "Course {course} not found"}}')
        return
    missions = c.get("pending_missions", [])
    if idx < 0 or idx >= len(missions):
        print(f'{{"error": "Mission index {idx} out of range"}}')
        return
    mission = missions.pop(idx)
    mission["completed"] = True
    mission["completed_date"] = datetime.now().isoformat()[:10]
    c.setdefault("completed_missions", []).append(mission)
    save(data)
    print(json.dumps({"completed": True, "mission": mission}))


def set_curriculum(course, curriculum_json_path):
    """Save a curriculum to the course data.

    Accepts a JSON file containing either a bare list of session objects
    or an object with a ``sessions`` key.
    """
    data = load()
    if not data:
        print('{"error": "No profile"}')
        return

    c = data["courses"].get(course)
    if not c:
        print(f'{{"error": "Course {course} not found"}}')
        return

    raw = json.loads(Path(curriculum_json_path).read_text())
    if isinstance(raw, list):
        sessions = raw
    elif isinstance(raw, dict) and "sessions" in raw:
        sessions = raw["sessions"]
    else:
        print('{"error": "Expected a JSON array or an object with a \\"sessions\\" key"}')
        return

    c["curriculum"] = sessions
    save(data)
    print(json.dumps({"saved": True, "course": course, "sessions": len(sessions)}))


def main():
    parser = argparse.ArgumentParser(description="Student progress tracker")
    sub = parser.add_subparsers(dest="cmd")

    p_init = sub.add_parser("init")
    p_init.add_argument("course")
    p_init.add_argument("name")

    p_show = sub.add_parser("show")
    p_show.add_argument("--concepts", action="store_true", help="Show concept mastery details")

    p_update = sub.add_parser("update")
    p_update.add_argument("course")
    p_update.add_argument("--session", type=int, required=True)
    p_update.add_argument("--score", type=int, required=True)
    p_update.add_argument("--max", type=int, required=True)
    p_update.add_argument("--concepts", type=str, default=None,
                          help='JSON object of concept scores, e.g. \'{"pod-basics": 0.9, "deployments": 0.6}\'')

    p_review = sub.add_parser("review")
    p_review.add_argument("course", nargs="?", default=None)

    p_achieve = sub.add_parser("achieve")
    p_achieve.add_argument("course")
    p_achieve.add_argument("id")
    p_achieve.add_argument("icon")
    p_achieve.add_argument("name")
    p_achieve.add_argument("description")

    p_mission = sub.add_parser("mission")
    p_mission.add_argument("course")
    p_mission.add_argument("description")

    p_mission_done = sub.add_parser("mission-complete")
    p_mission_done.add_argument("course")
    p_mission_done.add_argument("idx", type=int)

    p_curriculum = sub.add_parser("set-curriculum")
    p_curriculum.add_argument("course")
    p_curriculum.add_argument("curriculum_json", help="Path to curriculum JSON file")

    sub.add_parser("streak")
    sub.add_parser("xp")

    args = parser.parse_args()

    if args.cmd == "init":
        init_profile(args.name, args.course)
    elif args.cmd == "show":
        show(show_concepts=args.concepts)
    elif args.cmd == "update":
        update_session(args.course, args.session, args.score, args.max, args.concepts)
    elif args.cmd == "review":
        data = load()
        if data:
            due = get_review_concepts(data, args.course)
            print(json.dumps({"due_for_review": due, "count": len(due)}, indent=2))
        else:
            print('{"error": "No profile"}')
    elif args.cmd == "achieve":
        grant_achievement(args.course, args.id, args.icon, args.name, args.description)
    elif args.cmd == "mission":
        add_mission(args.course, args.description)
    elif args.cmd == "mission-complete":
        complete_mission(args.course, args.idx)
    elif args.cmd == "set-curriculum":
        set_curriculum(args.course, args.curriculum_json)
    elif args.cmd == "streak":
        data = load()
        if data:
            print(json.dumps({
                "streak_days": data.get("streak_days", 0),
                "last_session": data.get("last_session_date")
            }))
    elif args.cmd == "xp":
        data = load()
        if data:
            level, title = calculate_level(data.get("total_xp", 0))
            print(json.dumps({
                "total_xp": data.get("total_xp", 0),
                "level": level,
                "title": title
            }))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
