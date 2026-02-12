#!/usr/bin/env python3
"""
Build a lesson HTML file from a JSON config + shell template + component renderers.

Usage: uv run .agents/skills/interactive-learner/scripts/build-lesson.py <lesson.json> [--output <path>] [--open]
"""

import argparse
import html
import json
import random
import re
import subprocess
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SHELL_PATH = SKILL_DIR / "assets" / "shell.html"
COMPONENT_CSS_PATH = SKILL_DIR / "assets" / "components.css"
MERMAID_VERSION = "11.12.2"

MERMAID_COMPONENT_TYPES = {
    "concept-map",
    "mind-map",
    "kanban-board",
    "radar-profile",
}


def section_html(idx, inner_html):
    return f"""<div class="section" id="s{idx}">
{inner_html}
</div>"""


def sanitize_mermaid_id(raw, fallback="node"):
    value = str(raw or "").strip().lower()
    cleaned = re.sub(r"[^a-z0-9_]", "_", value)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    if not cleaned:
        cleaned = fallback
    if cleaned[0].isdigit():
        cleaned = f"n_{cleaned}"
    if cleaned in {"end", "subgraph", "graph", "flowchart"}:
        cleaned = f"{cleaned}_node"
    return cleaned


def escape_mermaid_label(text):
    return str(text or "").replace('"', '\\"').replace("\n", " ").strip()


def normalize_theme_css(theme_css):
    if not theme_css:
        return ""
    stripped = theme_css.strip()
    if stripped.startswith("<style"):
        return theme_css
    return f"<style>\n{theme_css}\n</style>"


def validate_renderer_output(section_type, renderer_output):
    if not isinstance(renderer_output, tuple) or len(renderer_output) != 2:
        raise ValueError(
            f"Renderer for '{section_type}' must return a tuple of (html_str, js_str)."
        )
    html_out, js_out = renderer_output
    if not isinstance(html_out, str) or not isinstance(js_out, str):
        raise ValueError(
            f"Renderer for '{section_type}' returned invalid output types."
        )


def build_mermaid_module_script():
    return f"""<script type="module">
import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@{MERMAID_VERSION}/dist/mermaid.esm.min.mjs";

const rootStyles = getComputedStyle(document.documentElement);
const token = (name, fallback) => rootStyles.getPropertyValue(name).trim() || fallback;

mermaid.initialize({{
  startOnLoad: false,
  securityLevel: "strict",
  theme: "base",
  themeVariables: {{
    darkMode: true,
    primaryColor: token("--card", "#121e34"),
    primaryTextColor: token("--text", "#d7e5ff"),
    primaryBorderColor: token("--accent", "#7ee3ff"),
    lineColor: token("--border-light", "#31507b"),
    secondaryColor: token("--bg-raised", "#0f1728"),
    tertiaryColor: token("--bg-inset", "#0a1321"),
    fontFamily: "Manrope, sans-serif",
    titleColor: token("--text", "#d7e5ff"),
    cScale0: token("--accent", "#7ee3ff"),
    cScale1: token("--green", "#84f0bf"),
    cScale2: token("--orange", "#ffc884"),
    cScale3: token("--pink", "#f3a6d8"),
    cScale4: token("--yellow", "#fbe58f"),
    radar: {{
      axisColor: token("--border-light", "#31507b"),
      axisStrokeWidth: 1,
      axisLabelFontSize: "12px",
      curveOpacity: 0.72,
      curveStrokeWidth: 2,
      graticuleColor: token("--border", "#223453"),
      graticuleOpacity: 0.5,
      graticuleStrokeWidth: 1,
      legendFontSize: "12px",
    }},
  }},
}});

try {{
  await mermaid.run({{ querySelector: ".mermaid" }});
}} catch (error) {{
  console.error("Mermaid rendering failed:", error);
}}
</script>"""


# -----------------------------------------------------------------------------
# COMPONENT RENDERERS — each returns (html_str, js_str)
# -----------------------------------------------------------------------------


def render_story_card(cfg, idx):
    variant = cfg.get("variant", "blue")
    if variant not in {"blue", "green", "orange", "cyan", "red", "pink"}:
        variant = "blue"
    label = html.escape(cfg.get("label", ""))
    content = cfg.get("content", "")

    h = section_html(
        idx,
        f"""<div class="story-card {variant}">
  <div class="story-label">{label}</div>
  {content}
</div>""",
    )
    return h, ""


def render_vocab_cards(cfg, idx):
    terms = cfg.get("terms", [])
    cards = ""
    for term in terms:
        icon = html.escape(str(term.get("icon", "📦")))
        term_name = html.escape(term.get("term", ""))
        definition = term.get("definition", "")
        analogy = term.get("analogy", "")
        what = term.get("what", "")
        why = term.get("why", "")
        how = term.get("how", "")
        watch_out = term.get("watch_out", "")

        detail_html = f"<p>{definition}</p>"
        if what:
            detail_html = f"<p><strong>What:</strong> {what}</p>"
            if why:
                detail_html += f"<p><strong>Why:</strong> {why}</p>"
            if how:
                detail_html += f"<p><strong>How:</strong> {how}</p>"
            if watch_out:
                detail_html += f"<p><strong>Watch out:</strong> {watch_out}</p>"

        analogy_block = (
            f'<div class="vocab-analogy"><strong>Analogy:</strong> {analogy}</div>'
            if analogy
            else ""
        )

        cards += f"""<div class="vocab-card" role="button" tabindex="0" onclick="this.classList.toggle('open')" onkeydown="if(event.key==='Enter' || event.key===' '){{ event.preventDefault(); this.classList.toggle('open'); }}">
  <div class="vocab-front">
    <span class="vocab-term">{icon} {term_name}</span>
    <span class="vocab-hint">tap to reveal ›</span>
  </div>
  <div class="vocab-back">{detail_html}{analogy_block}</div>
</div>
"""

    title = html.escape(cfg.get("title", "New Vocabulary"))
    h = section_html(
        idx,
        f"""<h2>{title}</h2>
<p>Click each card to reveal it.</p>
<div class="vocab-grid">{cards}</div>""",
    )
    return h, ""


def render_quiz(cfg, idx):
    questions = cfg.get("questions", [])
    quiz_html = ""
    for qi, question in enumerate(questions):
        qid = f"{idx}_{qi}"
        options_html = ""
        options = question.get("options", [])
        correct_idx = int(question.get("correct", 0))
        for oi, option in enumerate(options):
            is_correct = "true" if oi == correct_idx else "false"
            options_html += (
                f'<div class="quiz-opt" role="button" tabindex="0" onclick="quizAnswer(\'{qid}\', this, {is_correct})" '
                f'onkeydown="if(event.key===\'Enter\'||event.key===\' \'){{event.preventDefault();quizAnswer(\'{qid}\', this, {is_correct});}}">'
                f"{html.escape(str(option))}</div>\n"
            )

        feedback_correct = html.escape(question.get("feedback_correct", "Correct!"))
        feedback_wrong = html.escape(question.get("feedback_wrong", "Not quite."))
        q_text = question.get("question", "")

        quiz_html += f"""<div class="quiz-block" id="quiz_{qid}" data-fc="{feedback_correct}" data-fw="{feedback_wrong}">
  <div class="quiz-q">{qi + 1}. {q_text}</div>
  <div class="quiz-opts">{options_html}</div>
  <div class="quiz-fb" id="fb_{qid}"></div>
</div>
"""

    title = html.escape(cfg.get("title", "Quick Check"))
    h = section_html(idx, f"<h2>{title}</h2>\n{quiz_html}")
    js = """function quizAnswer(qid, el, correct) {
  const quiz = document.getElementById('quiz_' + qid);
  const fb = document.getElementById('fb_' + qid);
  const opts = quiz.querySelectorAll('.quiz-opt');
  if (opts[0] && opts[0].classList.contains('disabled')) return;

  opts.forEach((o) => {
    o.classList.add('disabled');
    if (o === el) o.classList.add(correct ? 'correct' : 'wrong');
  });

  if (!correct) {
    opts.forEach((o) => {
      if ((o.getAttribute('onclick') || '').includes('true')) {
        o.classList.add('correct');
      }
    });
  }

  fb.textContent = correct ? quiz.dataset.fc : quiz.dataset.fw;
  fb.className = 'quiz-fb show ' + (correct ? 'correct' : 'wrong');
  LES.score += correct ? 1 : 0;
  LES.maxScore += 1;
  addXp(correct ? 10 : 0);
  updateScore();
}"""
    return h, js


def render_matching(cfg, idx):
    pairs = cfg.get("pairs", [])
    title = html.escape(cfg.get("title", "Match the Concepts"))

    left_html = ""
    for pi, pair in enumerate(pairs):
        left_html += (
            f'<div class="m-item" role="button" tabindex="0" data-match="{pi}" onclick="mLeft(this, \'{idx}\')" '
            f'onkeydown="if(event.key===\'Enter\'||event.key===\' \'){{event.preventDefault();mLeft(this, \'{idx}\');}}">'
            f"{html.escape(str(pair.get('term', '')))}</div>\n"
        )

    right_order = cfg.get("right_order", list(reversed(range(len(pairs)))))
    right_html = ""
    for ri in right_order:
        pair = pairs[ri]
        right_html += (
            f'<div class="m-item" role="button" tabindex="0" data-match="{ri}" onclick="mRight(this, \'{idx}\')" '
            f'onkeydown="if(event.key===\'Enter\'||event.key===\' \'){{event.preventDefault();mRight(this, \'{idx}\');}}">'
            f"{html.escape(str(pair.get('definition', '')))}</div>\n"
        )

    total = len(pairs)
    h = section_html(
        idx,
        f"""<h2>{title}</h2>
<p>Click a term on the left, then its match on the right.</p>
<div class="m-game" id="match_{idx}" data-total="{total}">
  <div class="m-cols">
    <div class="m-left">{left_html}</div>
    <div class="m-right">{right_html}</div>
  </div>
  <div class="m-score" id="ms_{idx}">0 / {total}</div>
</div>""",
    )

    js = """const mSt = {};
function mLeft(el, gid) {
  if (el.classList.contains('matched')) return;
  document.querySelectorAll('#match_' + gid + ' .m-left .m-item').forEach((i) => i.classList.remove('selected'));
  el.classList.add('selected');
  if (!mSt[gid]) mSt[gid] = {};
  mSt[gid].left = el;
}

function mRight(el, gid) {
  if (!mSt[gid] || !mSt[gid].left || el.classList.contains('matched')) return;
  const left = mSt[gid].left;

  if (left.dataset.match === el.dataset.match) {
    left.classList.remove('selected');
    left.classList.add('matched');
    el.classList.add('matched');
    if (!mSt[gid].c) mSt[gid].c = 0;
    mSt[gid].c++;
    const total = parseInt(document.getElementById('match_' + gid).dataset.total, 10);
    document.getElementById('ms_' + gid).textContent = mSt[gid].c + ' / ' + total + (mSt[gid].c === total ? ' ✓' : '');
    LES.score += 1;
    LES.maxScore += 1;
    addXp(10);
    updateScore();
    mSt[gid].left = null;
  } else {
    el.classList.add('wrong-m');
    left.classList.add('wrong-m');
    setTimeout(() => {
      el.classList.remove('wrong-m');
      left.classList.remove('wrong-m');
    }, 400);
  }
}"""

    return h, js


def render_fill_blanks(cfg, idx):
    prompt = cfg.get("prompt", "Fill in the blanks:")
    template = cfg.get("template", "")
    slots = cfg.get("slots", [])
    choices = cfg.get("choices", [])

    rendered = template
    for slot in slots:
        slot_id = html.escape(slot.get("id", "slot"))
        answer = html.escape(str(slot.get("answer", "")))
        slot_html = (
            f'<span class="fb-slot" data-answer="{answer}" id="slot_{idx}_{slot_id}" '
            f'onclick="fbSlot(\'{idx}\', \'{slot_id}\')">???</span>'
        )
        rendered = rendered.replace("{{SLOT:" + slot.get("id", "") + "}}", slot_html)

    choices_html = "".join(
        f'<div class="fb-choice" role="button" tabindex="0" onclick="fbPick(this, \'{idx}\')" '
        f'onkeydown="if(event.key===\'Enter\'||event.key===\' \'){{event.preventDefault();fbPick(this, \'{idx}\');}}">'
        f"{html.escape(str(choice))}</div>\n"
        for choice in choices
    )

    title = html.escape(cfg.get("title", "Fill in the Blanks"))
    h = section_html(
        idx,
        f"""<h2>{title}</h2>
<p>{prompt}</p>
<div class="fb-game" id="fill_{idx}">
  <div class="fb-template">{rendered}</div>
  <div class="fb-choices">{choices_html}</div>
  <div class="fb-result" id="fill_fb_{idx}"></div>
</div>""",
    )

    success_msg = html.escape(cfg.get("success_message", "All correct!"))
    num_slots = len(slots)
    js = f"""const fbSt = {{}};
function fbSlot(gid, sid) {{
  const slot = document.getElementById('slot_' + gid + '_' + sid);
  if (slot.classList.contains('correct')) return;
  if (!fbSt[gid]) fbSt[gid] = {{}};
  document.querySelectorAll('#fill_' + gid + ' .fb-slot').forEach((s) => s.classList.remove('active'));
  slot.classList.add('active');
  fbSt[gid].active = sid;
}}

function fbPick(el, gid) {{
  if (!fbSt[gid] || !fbSt[gid].active) return;

  const sid = fbSt[gid].active;
  const slot = document.getElementById('slot_' + gid + '_' + sid);
  if (slot.classList.contains('correct')) return;

  const val = el.textContent;
  slot.textContent = val;
  slot.classList.add('filled');
  slot.classList.remove('active');

  if (val === slot.dataset.answer) {{
    slot.classList.remove('filled', 'wrong');
    slot.classList.add('correct');
    el.classList.add('used');
    if (!fbSt[gid].c) fbSt[gid].c = 0;
    fbSt[gid].c++;
    LES.score += 1;
    LES.maxScore += 1;
    addXp(15);
    updateScore();

    if (fbSt[gid].c === {num_slots}) {{
      const fb = document.getElementById('fill_fb_' + gid);
      fb.textContent = "{success_msg}";
      fb.className = 'fb-result show correct';
    }}
  }} else {{
    slot.classList.add('wrong');
    setTimeout(() => {{
      slot.classList.remove('filled', 'wrong');
      slot.textContent = '???';
    }}, 600);
  }}

  fbSt[gid].active = null;
}}"""

    return h, js


def render_side_by_side(cfg, idx):
    title = html.escape(cfg.get("title", "Comparison"))
    left = cfg.get("left", {})
    right = cfg.get("right", {})

    def render_column(col, cls):
        header = html.escape(str(col.get("header", "")))
        icon = html.escape(str(col.get("icon", "")))
        bullet = html.escape(str(col.get("bullet", "•")))
        items = col.get("items", [])
        items_html = "".join(
            f'<li><span class="cmp-b">{bullet}</span> {html.escape(str(item))}</li>'
            for item in items
        )
        return f"""<div class="cmp-col {cls}">
  <h3>{icon} {header}</h3>
  <ul>{items_html}</ul>
</div>"""

    h = section_html(
        idx,
        f"""<h2>{title}</h2>
<div class="cmp">{render_column(left, 'col-l')}{render_column(right, 'col-r')}</div>""",
    )
    return h, ""


def render_video_embed(cfg, idx):
    youtube_id = cfg.get("youtube_id", "")
    if not youtube_id:
        raise ValueError("video-embed requires 'youtube_id'.")

    start = int(cfg.get("start", 0) or 0)
    title = html.escape(cfg.get("title", "Watch This"))
    intro = html.escape(cfg.get("intro", ""))
    skip_label = html.escape(cfg.get("skip_label", "Skip video"))

    youtube_url = f"https://www.youtube.com/watch?v={youtube_id}"
    if start:
        youtube_url += f"&t={start}"
    thumbnail_url = f"https://img.youtube.com/vi/{youtube_id}/hqdefault.jpg"

    h = section_html(
        idx,
        f"""<h2>{title}</h2>
<p class="video-intro">{intro}</p>
<a href="{youtube_url}" target="_blank" rel="noopener" class="vid-thumb">
  <img src="{thumbnail_url}" alt="Video thumbnail" loading="lazy">
  <div class="vid-play">▶</div>
  <div class="vid-label">Watch on YouTube</div>
</a>
<p class="video-skip"><a href="#s{idx + 1}" class="video-skip-link">{skip_label} ↓</a></p>""",
    )
    return h, ""


def render_simulator(cfg, idx):
    title = html.escape(cfg.get("title", "Simulator"))
    description = cfg.get("description", "")
    entities = cfg.get("entities", [])
    actions = cfg.get("actions", [])
    handlers = cfg.get("handlers", {})

    entities_html = "".join(
        f'<div class="srv healthy" id="sim_{idx}_{html.escape(str(ent.get("id", "ent")))}">'
        f'<div class="srv-icon">{html.escape(str(ent.get("icon", "📦")))}</div>'
        f'<div class="srv-lbl">{html.escape(str(ent.get("label", "")))}</div>'
        "</div>\n"
        for ent in entities
    )

    buttons_html = ""
    for action in actions:
        action_type = " danger" if action.get("type") == "danger" else ""
        key = action.get("handler_key", "noop")
        label = html.escape(str(action.get("label", "Action")))
        icon = html.escape(str(action.get("icon", "")))
        buttons_html += (
            f'<button class="sim-btn{action_type}" onclick="sim_{idx}_{key}()">{icon} {label}</button>\n'
        )

    h = section_html(
        idx,
        f"""<h2>{title}</h2>
<p>{description}</p>
<div class="sim-wrap">
  <div class="srv-row" id="sim_viz_{idx}">{entities_html}</div>
  <div class="sim-btns">{buttons_html}</div>
  <div class="sim-log" id="sim_log_{idx}">
    <div class="entry"><span class="sim-log-tag success">[ready]</span> All systems running ✓</div>
  </div>
</div>""",
    )

    handler_js = "".join(f"function sim_{idx}_{k}(){{{v}}}\n" for k, v in handlers.items())
    helper_js = f"""function simLog_{idx}(msg, type) {{
  const log = document.getElementById('sim_log_{idx}');
  const normalized = (type || 'info').toLowerCase();
  log.innerHTML += '<div class="entry"><span class="sim-log-tag ' + normalized + '">[' + normalized + ']</span> ' + msg + '</div>';
  log.scrollTop = log.scrollHeight;
}}\n"""

    return h, helper_js + handler_js


def render_sorting_game(cfg, idx):
    title = html.escape(cfg.get("title", "Put These in Order"))
    prompt = html.escape(cfg.get("prompt", "Drag to reorder:"))
    items = cfg.get("items", [])

    order = list(range(len(items)))
    random.shuffle(order)

    items_html = "".join(
        f'<div class="sort-it" draggable="true" data-correct="{di}" data-idx="{di}">'
        f'<span class="sort-grip">⠿</span>{html.escape(str(items[di]))}</div>\n'
        for di in order
    )

    correct_json = json.dumps(list(range(len(items))))
    h = section_html(
        idx,
        f"""<h2>{title}</h2>
<p>{prompt}</p>
<div class="sort-game" id="sort_{idx}" data-correct='{correct_json}'>
  <div class="sort-list" id="sl_{idx}">{items_html}</div>
  <button class="sim-btn sort-check-btn" onclick="chkSort('{idx}')">Check order</button>
  <div class="fb-result" id="sfb_{idx}"></div>
</div>""",
    )

    js = f"""(function() {{
  const list = document.getElementById('sl_{idx}');
  let dragEl = null;

  list.addEventListener('dragstart', (event) => {{
    dragEl = event.target.closest('.sort-it');
    if (dragEl) dragEl.classList.add('dragging');
  }});

  list.addEventListener('dragend', () => {{
    if (dragEl) dragEl.classList.remove('dragging');
    dragEl = null;
  }});

  list.addEventListener('dragover', (event) => {{
    event.preventDefault();
    if (!dragEl) return;
    const after = getAfter(list, event.clientY);
    if (!after) list.appendChild(dragEl);
    else list.insertBefore(dragEl, after);
  }});

  function getAfter(container, y) {{
    return [...container.querySelectorAll('.sort-it:not(.dragging)')].reduce((closest, child) => {{
      const box = child.getBoundingClientRect();
      const offset = y - box.top - box.height / 2;
      return offset < 0 && offset > closest.offset ? {{ offset, element: child }} : closest;
    }}, {{ offset: -Infinity }}).element;
  }}
}})();

function chkSort(gid) {{
  const list = document.getElementById('sl_' + gid);
  const items = [...list.querySelectorAll('.sort-it')];
  const correct = JSON.parse(document.getElementById('sort_' + gid).dataset.correct);
  let ok = true;

  items.forEach((item, i) => {{
    item.classList.remove('correct-pos', 'wrong-pos');
    if (parseInt(item.dataset.correct, 10) === correct[i]) item.classList.add('correct-pos');
    else {{
      item.classList.add('wrong-pos');
      ok = false;
    }}
  }});

  const fb = document.getElementById('sfb_' + gid);
  if (ok) {{
    fb.textContent = 'Correct order!';
    fb.className = 'fb-result show correct';
    LES.score += 1;
    LES.maxScore += 1;
    addXp(15);
    updateScore();
  }} else {{
    fb.textContent = 'Not quite — rearrange and try again.';
    fb.className = 'fb-result show wrong';
  }}
}}"""

    return h, js


def render_timeline(cfg, idx):
    title = html.escape(cfg.get("title", "Timeline"))
    events = cfg.get("events", [])
    events_html = ""
    for event in events:
        icon = html.escape(str(event.get("icon", "·")))
        date = html.escape(str(event.get("date", "")))
        event_title = html.escape(str(event.get("title", "")))
        desc = event.get("description", "")
        events_html += f"""<div class="tl-ev">
  <div class="tl-dot">{icon}</div>
  <div class="tl-date">{date}</div>
  <div class="tl-name">{event_title}</div>
  <div class="tl-desc">{desc}</div>
</div>
"""

    h = section_html(
        idx,
        f"""<h2>{title}</h2>
<div class="tl-scroll"><div class="tl-track">{events_html}</div></div>""",
    )
    return h, ""


def render_concept_map(cfg, idx):
    title = html.escape(cfg.get("title", "Concept Map"))
    mermaid_code = cfg.get("mermaid", "")
    if not mermaid_code:
        nodes = cfg.get("nodes", [])
        edges = cfg.get("edges", [])
        lines = ["graph TD"]
        node_ids = []
        for ni, node in enumerate(nodes):
            raw_id = node.get("id", f"node_{ni + 1}")
            node_id = sanitize_mermaid_id(raw_id, f"node_{ni + 1}")
            label = escape_mermaid_label(node.get("label", node_id))
            icon = escape_mermaid_label(node.get("icon", ""))
            display = f"{icon} {label}".strip()
            node_ids.append(node_id)
            lines.append(f'  {node_id}["{display}"]')

        if edges:
            for edge in edges:
                frm = sanitize_mermaid_id(edge.get("from", ""), "from")
                to = sanitize_mermaid_id(edge.get("to", ""), "to")
                edge_label = edge.get("label", "")
                if edge_label:
                    lbl = escape_mermaid_label(edge_label)
                    lines.append(f'  {frm} -->|"{lbl}"| {to}')
                else:
                    lines.append(f"  {frm} --> {to}")
        elif len(node_ids) > 1:
            for i in range(len(node_ids) - 1):
                lines.append(f"  {node_ids[i]} --> {node_ids[i + 1]}")
        mermaid_code = "\n".join(lines)

    escaped = html.escape(mermaid_code)
    h = section_html(
        idx,
        f"""<h2>{title}</h2>
<div class="mermaid-wrap">
  <pre class="mermaid">{escaped}</pre>
</div>""",
    )
    return h, ""


def _walk_mind_tree(node, depth, lines, index_prefix="n"):
    if isinstance(node, str):
        label = escape_mermaid_label(node)
        node_id = sanitize_mermaid_id(f"{index_prefix}_{depth}_{label[:12]}", f"node_{depth}")
        lines.append(f'{"  " * depth}{node_id}["{label}"]')
        return
    if not isinstance(node, dict):
        return
    label = escape_mermaid_label(node.get("text", "Node"))
    node_id = sanitize_mermaid_id(node.get("id") or f"{index_prefix}_{depth}_{label[:12]}", f"node_{depth}")
    lines.append(f'{"  " * depth}{node_id}["{label}"]')
    for ci, child in enumerate(node.get("children", [])):
        _walk_mind_tree(child, depth + 1, lines, f"{node_id}_{ci}")


def render_mind_map(cfg, idx):
    title = html.escape(cfg.get("title", "Mind Map"))
    subtitle = html.escape(cfg.get("subtitle", ""))
    mermaid_code = cfg.get("mermaid", "")
    if not mermaid_code:
        root_text = cfg.get("root", "Main Topic")
        branches = cfg.get("branches", [])
        lines = ["mindmap"]
        root_node = {"text": root_text, "children": branches}
        _walk_mind_tree(root_node, 1, lines)
        mermaid_code = "\n".join(lines)
    escaped = html.escape(mermaid_code)
    subtitle_html = f'<p class="mindmap-help">{subtitle}</p>' if subtitle else ""
    h = section_html(
        idx,
        f"""<h2>{title}</h2>
<div class="mermaid-wrap">
  <pre class="mermaid">{escaped}</pre>
</div>
{subtitle_html}""",
    )
    return h, ""


def _safe_bracket_text(value):
    return str(value or "").replace("]", ")").replace("\n", " ")


def render_kanban_board(cfg, idx):
    title = html.escape(cfg.get("title", "Kanban Board"))
    subtitle = html.escape(cfg.get("subtitle", ""))
    columns = cfg.get("columns", [])
    ticket_base_url = cfg.get("ticket_base_url", "")

    lines = ["kanban"]
    for ci, column in enumerate(columns):
        col_id = sanitize_mermaid_id(column.get("id", f"column_{ci + 1}"), f"column_{ci + 1}")
        col_title = _safe_bracket_text(column.get("title", f"Column {ci + 1}"))
        lines.append(f"  {col_id}[{col_title}]")
        for ti, task in enumerate(column.get("tasks", [])):
            task_data = {"title": task} if isinstance(task, str) else task
            task_id = sanitize_mermaid_id(task_data.get("id", f"task_{ci + 1}_{ti + 1}"), f"task_{ci + 1}_{ti + 1}")
            task_title = _safe_bracket_text(task_data.get("title", f"Task {ti + 1}"))
            task_line = f"    {task_id}[{task_title}]"
            metadata = []
            for key in ("assigned", "ticket", "priority"):
                val = task_data.get(key)
                if val:
                    escaped_val = str(val).replace('"', '\\"')
                    metadata.append(f'{key}: "{escaped_val}"')
            if metadata:
                task_line += "@{ " + ", ".join(metadata) + " }"
            lines.append(task_line)

    if ticket_base_url:
        safe_url = str(ticket_base_url).replace('"', '\\"')
        frontmatter = [
            "---",
            "config:",
            "  kanban:",
            f'    ticketBaseUrl: "{safe_url}"',
            "---",
        ]
        mermaid_code = "\n".join(frontmatter + lines)
    else:
        mermaid_code = "\n".join(lines)

    escaped = html.escape(mermaid_code)
    subtitle_html = f'<p class="kanban-help">{subtitle}</p>' if subtitle else ""
    h = section_html(
        idx,
        f"""<h2>{title}</h2>
<div class="mermaid-wrap">
  <pre class="mermaid">{escaped}</pre>
</div>
{subtitle_html}""",
    )
    return h, ""


def render_radar_profile(cfg, idx):
    title = html.escape(cfg.get("title", "Radar Profile"))
    subtitle = html.escape(cfg.get("subtitle", ""))
    axes = cfg.get("axes", [])
    curves = cfg.get("curves", [])
    if not axes:
        raise ValueError("radar-profile requires an 'axes' array.")

    axis_defs = []
    axis_ids = []
    for ai, axis in enumerate(axes):
        if isinstance(axis, str):
            label = axis
            axis_id = sanitize_mermaid_id(label, f"axis_{ai + 1}")
        else:
            label = axis.get("label", f"Axis {ai + 1}")
            axis_id = sanitize_mermaid_id(axis.get("id", label), f"axis_{ai + 1}")
        axis_ids.append(axis_id)
        axis_defs.append(f'axis {axis_id}["{escape_mermaid_label(label)}"]')

    lines = ["radar-beta"]
    if cfg.get("chart_title"):
        lines.append(f'title "{escape_mermaid_label(cfg.get("chart_title"))}"')
    lines.extend(axis_defs)

    for ci, curve in enumerate(curves):
        curve_id = sanitize_mermaid_id(curve.get("id", f"curve_{ci + 1}"), f"curve_{ci + 1}")
        curve_label = escape_mermaid_label(curve.get("label", curve_id))
        values = curve.get("values", [])
        if isinstance(values, dict):
            points = [f"{axis_id}: {values.get(axis_id, 0)}" for axis_id in axis_ids]
            points_str = ", ".join(points)
        else:
            normalized = [str(values[i]) if i < len(values) else "0" for i in range(len(axis_ids))]
            points_str = ", ".join(normalized)
        lines.append(f'curve {curve_id}["{curve_label}"]{{{points_str}}}')

    if "show_legend" in cfg:
        lines.append(f"showLegend {'true' if cfg.get('show_legend') else 'false'}")
    if cfg.get("max") is not None:
        lines.append(f"max {cfg.get('max')}")
    if cfg.get("min") is not None:
        lines.append(f"min {cfg.get('min')}")
    if cfg.get("graticule"):
        lines.append(f"graticule {cfg.get('graticule')}")
    if cfg.get("ticks") is not None:
        lines.append(f"ticks {cfg.get('ticks')}")

    mermaid_code = "\n".join(lines)
    escaped = html.escape(mermaid_code)
    subtitle_html = f'<p class="radar-help">{subtitle}</p>' if subtitle else ""
    h = section_html(
        idx,
        f"""<h2>{title}</h2>
<div class="mermaid-wrap">
  <pre class="mermaid">{escaped}</pre>
</div>
{subtitle_html}""",
    )
    return h, ""


def render_explain_back(cfg, idx):
    title = html.escape(cfg.get("title", "Teach It Back"))
    prompt = cfg.get("prompt", "Explain the concept in your own words.")
    hint = cfg.get("hint", "")
    concept = html.escape(cfg.get("concept", ""))
    criteria = cfg.get("eval_criteria", "")
    hint_html = f'<div class="oa-hint"><strong>Hint:</strong> {hint}</div>' if hint else ""
    meta_parts = []
    if concept:
        meta_parts.append(f"Concept: {concept}")
    if criteria:
        meta_parts.append("Evaluation criteria available in debrief")
    meta_html = f'<p class="oa-meta">{" · ".join(meta_parts)}</p>' if meta_parts else ""
    h = section_html(
        idx,
        f"""<h2>{title}</h2>
<div class="oa-card">
  <p class="oa-prompt">{prompt}</p>
  {hint_html}
  {meta_html}
</div>""",
    )
    return h, ""


def render_debug_challenge(cfg, idx):
    title = html.escape(cfg.get("title", "Find the Bug"))
    bug_description = cfg.get("bug_description", "Find the bug and explain why it fails.")
    language = html.escape(cfg.get("language", "text"))
    broken_code = html.escape(cfg.get("broken_code", ""))
    hint = cfg.get("hint", "")
    answer = cfg.get("correct_explanation", "")
    hint_html = f'<div class="oa-hint"><strong>Hint:</strong> {hint}</div>' if hint else ""
    answer_html = (
        f'<div class="debug-answer" id="dbg_answer_{idx}"><strong>Explanation:</strong> {answer}</div>'
        if answer
        else ""
    )
    h = section_html(
        idx,
        f"""<h2>{title}</h2>
<div class="oa-card">
  <p>{bug_description}</p>
  <pre class="debug-code"><code class="language-{language}">{broken_code}</code></pre>
  {hint_html}
  <button class="sim-btn debug-reveal" onclick="toggleDebugAnswer_{idx}()">Reveal explanation</button>
  {answer_html}
</div>""",
    )
    js = f"""function toggleDebugAnswer_{idx}() {{
  const el = document.getElementById('dbg_answer_{idx}');
  if (!el) return;
  el.classList.toggle('show');
}}"""
    return h, js


def render_roleplay(cfg, idx):
    title = html.escape(cfg.get("title", "Roleplay"))
    scenario = cfg.get("scenario", "")
    prompt = cfg.get("prompt", "How would you respond?")
    context = cfg.get("context", "")
    concept = html.escape(cfg.get("concept", ""))
    context_html = f'<div class="oa-hint"><strong>Context:</strong> {context}</div>' if context else ""
    concept_html = f'<p class="oa-meta">Concept: {concept}</p>' if concept else ""
    h = section_html(
        idx,
        f"""<h2>{title}</h2>
<div class="oa-card">
  <p><strong>Scenario:</strong> {scenario}</p>
  <p class="oa-prompt">{prompt}</p>
  {context_html}
  {concept_html}
</div>""",
    )
    return h, ""


def render_open_reflection(cfg, idx):
    title = html.escape(cfg.get("title", "Reflect"))
    prompt = cfg.get("prompt", "What did you learn and where can you apply it?")
    context = cfg.get("context", "")
    context_html = f'<div class="oa-hint">{context}</div>' if context else ""
    h = section_html(
        idx,
        f"""<h2>{title}</h2>
<div class="oa-card">
  <p class="oa-prompt">{prompt}</p>
  {context_html}
</div>""",
    )
    return h, ""


def render_real_world_mission(cfg, idx):
    title = html.escape(cfg.get("title", "Hands-On Mission"))
    mission = cfg.get("mission", "")
    url = cfg.get("url", "")
    context = cfg.get("context", "")
    followup = cfg.get("followup", "")
    mission_type = html.escape(cfg.get("mission_type", "mission").replace("-", " ").title())
    link_html = f'<a class="mission-link" href="{url}" target="_blank" rel="noopener">Open mission resource →</a>' if url else ""
    context_html = f'<div class="oa-hint"><strong>Context:</strong> {context}</div>' if context else ""
    followup_html = f'<p class="oa-meta"><strong>Follow-up:</strong> {followup}</p>' if followup else ""
    h = section_html(
        idx,
        f"""<h2>{title}</h2>
<div class="oa-card mission-grid">
  <p class="oa-meta">Mission type: {mission_type}</p>
  <p class="oa-prompt">{mission}</p>
  {link_html}
  {context_html}
  {followup_html}
</div>""",
    )
    return h, ""


def render_recommended_deep_dive(cfg, idx):
    title = html.escape(cfg.get("title", "Recommended Deep Dive"))
    resources = cfg.get("resources", [])
    items_html = ""
    for resource in resources:
        r_type = html.escape(str(resource.get("type", "resource")))
        r_title = html.escape(str(resource.get("title", "Untitled resource")))
        url = resource.get("url", "")
        why = html.escape(str(resource.get("why", "")))
        duration = html.escape(str(resource.get("duration", "")))
        author = html.escape(str(resource.get("author", "")))
        title_html = (
            f'<a class="deep-dive-link" href="{url}" target="_blank" rel="noopener">{r_title}</a>'
            if url
            else f'<span class="deep-dive-link">{r_title}</span>'
        )
        extra = f" · {author}" if author else ""
        duration_html = f'<span class="deep-dive-duration">{duration}{extra}</span>' if (duration or author) else ""
        items_html += f"""<div class="deep-dive-item">
  <div class="deep-dive-top">
    <span class="deep-dive-type">{r_type}</span>
    {duration_html}
  </div>
  {title_html}
  <p class="deep-dive-why">{why}</p>
</div>
"""
    h = section_html(
        idx,
        f"""<h2>{title}</h2>
<div class="deep-dive-list">{items_html}</div>""",
    )
    return h, ""


def render_community_challenge(cfg, idx):
    title = html.escape(cfg.get("title", "Community Challenge"))
    challenge = cfg.get("challenge", "")
    context = cfg.get("context", "")
    followup = cfg.get("followup", "")
    context_html = f'<div class="oa-hint"><strong>Context:</strong> {context}</div>' if context else ""
    followup_html = f'<p class="oa-meta"><strong>Follow-up:</strong> {followup}</p>' if followup else ""
    h = section_html(
        idx,
        f"""<h2>{title}</h2>
<div class="oa-card">
  <p class="oa-prompt">{challenge}</p>
  {context_html}
  {followup_html}
</div>""",
    )
    return h, ""


def render_score_summary(cfg, idx):
    title = html.escape(cfg.get("title", "Session Complete!"))
    learned = cfg.get("learned", [])
    next_preview = cfg.get("next_preview", "")
    vocab_total = cfg.get("vocab_total", 0)
    missions_pending = cfg.get("missions_pending", [])

    learned_html = "".join(f"<li>{item}</li>" for item in learned)
    next_html = ""
    if next_preview:
        next_html = f"""<div class="story-card blue summary-next">
  <div class="story-label">Next Session</div>
  <p>{next_preview}</p>
</div>"""
    vocab_html = (
        f'<p class="score-vocab">Running vocabulary: {int(vocab_total)} terms</p>'
        if vocab_total
        else ""
    )
    missions_html = ""
    if missions_pending:
        mission_items = "".join(f"<li>{html.escape(str(mission))}</li>" for mission in missions_pending)
        missions_html = f"""<div class="story-card cyan summary-missions">
  <div class="story-label">Pending Missions</div>
  <ul>{mission_items}</ul>
</div>"""

    h = section_html(
        idx,
        f"""<h2>🏁 {title}</h2>
<div class="score-box" id="scoreSummary">
  <div class="score-lbl">YOUR SCORE</div>
  <div class="score-num" id="finalScore">—</div>
  <div class="score-msg" id="scoreLabel">Complete the exercises above</div>
  <div class="score-xp" id="scoreXp"></div>
  {vocab_html}
</div>
<div class="story-card green">
  <div class="story-label">What You Learned</div>
  <ul class="summary-learned-list">{learned_html}</ul>
</div>
{next_html}
{missions_html}
<p class="summary-footnote">Head back to Claude to continue!</p>""",
    )

    js = """function updateScore() {
  const scoreEl = document.getElementById('finalScore');
  if (!scoreEl || LES.maxScore <= 0) return;

  scoreEl.textContent = LES.score + ' / ' + LES.maxScore;
  scoreEl.style.animation = 'counter-bump 0.3s ease';
  setTimeout(() => (scoreEl.style.animation = ''), 300);

  const pct = Math.round((LES.score / LES.maxScore) * 100);
  let label = '';

  if (pct === 100) {
    label = 'Perfect score!';
    if (!LES.confettiLaunched) {
      launchConfetti();
      LES.confettiLaunched = true;
    }
  } else if (pct >= 80) {
    label = 'Excellent work!';
    LES.confettiLaunched = false;
  } else if (pct >= 60) {
    label = 'Good job! Keep at it.';
    LES.confettiLaunched = false;
  } else {
    label = 'Nice try — review and retry.';
    LES.confettiLaunched = false;
  }

  document.getElementById('scoreLabel').textContent = label;
  document.getElementById('scoreXp').textContent = '⚡ ' + LES.xp + ' XP this session';
}"""
    return h, js


def render_custom(cfg, idx):
    raw_html = cfg.get("html", "")
    raw_js = cfg.get("js", "")
    raw_css = cfg.get("css", "")
    css_block = f"<style>{raw_css}</style>" if raw_css else ""
    h = section_html(idx, css_block + raw_html)
    return h, raw_js


RENDERERS = {
    "story-card": render_story_card,
    "vocab-cards": render_vocab_cards,
    "quiz": render_quiz,
    "matching": render_matching,
    "fill-blanks": render_fill_blanks,
    "side-by-side": render_side_by_side,
    "video-embed": render_video_embed,
    "simulator": render_simulator,
    "sorting-game": render_sorting_game,
    "timeline": render_timeline,
    "concept-map": render_concept_map,
    "mind-map": render_mind_map,
    "kanban-board": render_kanban_board,
    "radar-profile": render_radar_profile,
    "explain-back": render_explain_back,
    "debug-challenge": render_debug_challenge,
    "roleplay": render_roleplay,
    "open-reflection": render_open_reflection,
    "real-world-mission": render_real_world_mission,
    "recommended-deep-dive": render_recommended_deep_dive,
    "community-challenge": render_community_challenge,
    "score-summary": render_score_summary,
    "custom": render_custom,
}


def build_lesson(config, output_path=None):
    shell = SHELL_PATH.read_text()
    component_css = COMPONENT_CSS_PATH.read_text()

    sections_parts = []
    script_parts = []
    script_seen = set()
    use_mermaid = False

    for idx, section in enumerate(config.get("sections", []), start=1):
        section_type = section.get("type")
        if not section_type:
            raise ValueError(f"Section {idx} is missing required field 'type'.")
        renderer = RENDERERS.get(section_type)
        if renderer is None:
            supported = ", ".join(sorted(RENDERERS.keys()))
            raise ValueError(
                f"Unknown section type '{section_type}' in section {idx}. Supported types: {supported}."
            )

        rendered = renderer(section, idx)
        validate_renderer_output(section_type, rendered)
        section_html_out, section_js_out = rendered

        sections_parts.append(section_html_out)
        sections_parts.append('<div class="divider"></div>')
        if section_js_out and section_js_out not in script_seen:
            script_parts.append(section_js_out)
            script_seen.add(section_js_out)
        if section_type in MERMAID_COMPONENT_TYPES:
            use_mermaid = True

    module_scripts = build_mermaid_module_script() if use_mermaid else ""

    result = shell
    result = result.replace("{{TITLE}}", html.escape(str(config.get("title", "Lesson"))))
    result = result.replace("{{SUBTITLE}}", html.escape(str(config.get("subtitle", ""))))
    result = result.replace("{{COURSE_NAME}}", html.escape(str(config.get("course_name", "Lesson"))))
    result = result.replace("{{SESSION_NUM}}", str(config.get("session", 1)))
    result = result.replace("{{ESTIMATED_MINUTES}}", str(config.get("estimated_minutes", 15)))
    result = result.replace("{{XP_START}}", str(config.get("xp_start", 0)))
    result = result.replace("{{XP_DISPLAY}}", f"⚡ {config.get('xp_start', 0)} XP")
    result = result.replace("{{COMPONENT_CSS}}", component_css)
    result = result.replace("{{THEME_CSS}}", normalize_theme_css(config.get("theme_css", "")))
    result = result.replace("{{SECTIONS}}", "\n".join(sections_parts))
    result = result.replace("{{COMPONENT_SCRIPTS}}", "\n".join(script_parts))
    result = result.replace("{{MODULE_SCRIPTS}}", module_scripts)

    out_path = Path(output_path) if output_path else (Path.cwd() / f"lesson-{config.get('session', 1)}.html")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(result)
    return str(out_path)


def main():
    parser = argparse.ArgumentParser(description="Build a lesson HTML from JSON config")
    parser.add_argument("config", help="Path to lesson JSON config file")
    parser.add_argument("--output", "-o", help="Output HTML file path")
    parser.add_argument("--open", action="store_true", help="Open in browser after building")
    args = parser.parse_args()

    with open(args.config, encoding="utf-8") as f:
        config = json.load(f)

    out = build_lesson(config, args.output)
    print(f"✅ Lesson built: {out}")

    if args.open:
        import platform

        cmd = {"Darwin": ["open"], "Linux": ["xdg-open"]}.get(platform.system(), ["start"])
        subprocess.run(cmd + [out], shell=(platform.system() == "Windows"))


if __name__ == "__main__":
    main()
