# Component Catalog

Reference for all available lesson components. Each component is rendered by `build-lesson.py` from a JSON config.

## Two-Phase Model

Each session produces two HTML files:

- **Explainer phase** (`--mode explainer`): Content-only components that teach the material. Allowed: `story-card`, `vocab-cards`, `side-by-side`, `video-embed`, `timeline`, `concept-map`, `mind-map`, `kanban-board`, `radar-profile`, `recommended-deep-dive`, `debug-challenge`, `simulator`, `real-world-mission`, `community-challenge`, `custom`.
- **Test phase** (`--mode test`): Scored exercise components that assess understanding. Allowed: `quiz`, `matching`, `fill-blanks`, `sorting-game`, `score-summary`, `custom`.
- **Conversational** (not in HTML): `explain-back`, `roleplay`, `open-reflection` — asked by the agent in chat between the explainer and test phases.

If `--mode` is set and a section uses a disallowed component type, `build-lesson.py` raises a clear error.

### HTML vs Plain Text Fields

Some fields are rendered as raw HTML (allowing `<code>`, `<strong>`, links, etc.), while others are escaped to plain text.

- **HTML fields:** story-card `content`, side-by-side `items`, timeline `description`, vocab-cards detail fields (`definition`, `analogy`, `what`, `why`, `how`, `watch_out`), debug-challenge `bug_description`/`hint`/`correct_explanation`, real-world-mission/community-challenge body fields (`mission`, `context`, `followup`, `challenge`), custom `html`
- **Plain text fields:** all `title` and `label` fields, quiz `question`/`options`/feedback, matching `term`/`definition`, fill-blanks `slots`/`choices`, sorting-game `items`, side-by-side `header`/`bullet`

When using HTML fields, you can include inline HTML like `<code>ls -la</code>`, `<strong>important</strong>`, or `<a href="...">links</a>`.

---

## Core Components (click-based, scored — test phase)

### quiz
Multiple choice questions with instant feedback. The workhorse assessment component.
```json
{"type": "quiz", "title": "Quick Check", "questions": [
  {"question": "What is a Pod?", "options": ["A server", "A container wrapper", "A network"], "correct": 1,
   "feedback_correct": "Right! Pods wrap one or more containers.", "feedback_wrong": "Not quite — a Pod wraps containers so Kubernetes can manage them.",
   "concept": "pod-basics"}
]}
```
- `concept` (optional): ties this question to a tracked concept for mastery data
- Tip: use "predict before you learn" quizzes at session start — quiz BEFORE explaining

### matching
Connect pairs by clicking left then right. Great for vocabulary, concept mapping, cause-and-effect.
```json
{"type": "matching", "title": "Match the Concepts", "pairs": [
  {"term": "Cluster", "definition": "The whole system"},
  {"term": "Node", "definition": "A single machine"}
], "right_order": [1, 0]}
```

### fill-blanks
Click slots then pick values. Excellent for building configs, code, formulas, sentences.
```json
{"type": "fill-blanks", "title": "Build a Deployment", "prompt": "Fill in the Kubernetes config:",
 "template": "kind: {{SLOT:kind}}\nspec:\n  replicas: {{SLOT:count}}",
 "slots": [{"id": "kind", "answer": "Deployment", "concept": "deployments"}, {"id": "count", "answer": "3"}],
 "choices": ["Deployment", "Service", "3", "5"],
 "success_message": "Valid Kubernetes config!"}
```

### sorting-game
Drag items into correct order. Items provided in correct order, shuffled automatically.
```json
{"type": "sorting-game", "title": "Order of Operations", "prompt": "Put these deployment steps in order:",
 "items": ["Write Dockerfile", "Build image", "Push to registry", "Create Deployment YAML", "kubectl apply"]}
```

### simulator
Custom simulation with entities, buttons, and log. Handlers are raw JS. Use for complex interactive demonstrations.
```json
{"type": "simulator", "title": "Container Crash Sim",
 "description": "See what happens when containers fail",
 "entities": [{"id": "web1", "label": "Web App 1", "icon": "🐳"}],
 "actions": [{"label": "Kill Container", "icon": "💥", "type": "danger", "handler_key": "crash"}],
 "handlers": {"crash": "const el=document.querySelector('.srv.healthy'); if(el){el.classList.remove('healthy');el.classList.add('crashed');el.querySelector('.srv-icon').textContent='💀';simLog_5('Container web1 crashed!','error');}"}}
```

**Available in handlers:**
- `simLog_{idx}(msg, type)` — append to the simulator log. `type` can be `"info"`, `"error"`, `"success"`, or `"warning"`. The `{idx}` is the section index (1-based position in the `sections` array).
- Entity DOM IDs follow the pattern: `sim_{idx}_{entity_id}` (e.g., `sim_5_web1`)
- CSS classes on entities: `srv` (base), `healthy` (initial state). Add `crashed`, `warning`, etc. in handlers.

---

## Content Components (explanatory, non-scored — explainer phase)

### story-card
Narrative block with colored sidebar. Use for explanations, scenarios, recaps, motivating stories.
```json
{"type": "story-card", "variant": "blue|green|orange|cyan|red|pink", "label": "KEY POINT", "content": "<p>HTML content here</p>"}
```
Variants: `blue` (info), `green` (success/good practice), `orange` (warning/gotcha), `cyan` (analogy), `red` (critical/danger), `pink` (fun fact/aside).

### vocab-cards
Click-to-reveal flip cards. Use for new terminology (max 6 per session).
```json
{"type": "vocab-cards", "title": "New Vocabulary", "terms": [
  {"term": "Pod", "icon": "🫛", "definition": "The smallest unit...", "analogy": "Like a lunch box for your containers",
   "what": "A wrapper around containers", "why": "K8s needs a manageable unit", "how": "Created via Deployments", "watch_out": "Pods are disposable",
   "concept": "pod-basics"}
]}
```
Supports both simple (definition+analogy) and structured (what/why/how/watch_out) formats. `concept` field ties to mastery tracking.

### side-by-side
Two-column comparison. Use for before/after, tool A vs B, wrong vs right.
```json
{"type": "side-by-side", "title": "Docker vs Kubernetes",
 "left": {"header": "Docker Alone", "icon": "🐳", "items": ["You manage everything", "Manual restarts"], "bullet": "🐳"},
 "right": {"header": "With Kubernetes", "icon": "☸️", "items": ["Automated management", "Self-healing"], "bullet": "☸️"}}
```

### video-embed
YouTube video thumbnail with click-to-watch link. Use for short, curated videos (max 2 per lesson). Pair with `recommended-deep-dive` for optional extras.
```json
{"type": "video-embed", "youtube_id": "dQw4w9WgXcQ", "title": "Watch This",
 "intro": "This 5-minute video nails the mental model.",
 "start": 30, "skip_label": "Skip video"}
```
- `youtube_id` (required): the YouTube video ID (the part after `v=`)
- `title` (optional, default `"Watch This"`): heading above the thumbnail
- `intro` (optional): short text above the thumbnail explaining why to watch
- `start` (optional, default `0`): start time in seconds
- `skip_label` (optional, default `"Skip video"`): text for the skip link

### timeline
Horizontal scrollable timeline. Use for history, processes, evolution, sequences.
```json
{"type": "timeline", "title": "History of Containers", "events": [
  {"date": "2013", "title": "Docker launched", "description": "Containers go mainstream", "icon": "🐳"},
  {"date": "2014", "title": "Kubernetes announced", "description": "Google open-sources K8s", "icon": "☸️"}
]}
```

### concept-map
Mermaid.js diagram rendered client-side. Use for showing relationships between ideas.

**Option A: Structured nodes + edges** (recommended):
```json
{"type": "concept-map", "title": "How K8s Pieces Connect", "nodes": [
  {"id": "cluster", "label": "Cluster", "icon": "☸️"},
  {"id": "node", "label": "Node", "icon": "🖥️"}
], "edges": [
  {"from": "cluster", "to": "node", "label": "contains"}
]}
```

**Option B: Raw Mermaid string** (for complex diagrams):
```json
{"type": "concept-map", "title": "Architecture", "mermaid": "graph TD\n  A[Client] --> B[API Server]\n  B --> C[etcd]\n  B --> D[Scheduler]"}
```

**Direction guidance:** Always use `graph TD` (top-down) for concept maps. The lesson container is portrait-oriented, so `graph LR` (left-right) produces diagrams that are too wide and collapse to an unreadable size.

### mind-map
Mermaid.js mindmap (hierarchical overview). Use for topic maps, prerequisite trees, and conceptual scaffolding.
```json
{"type": "mind-map", "title": "Kubernetes Learning Map",
 "root": "Kubernetes",
 "branches": [
   {"text": "Core objects", "children": ["Pod", "Deployment", "Service"]},
   {"text": "Control plane", "children": ["API server", "Scheduler", "Controller manager"]},
   {"text": "Operations", "children": ["Observability", "Scaling", "Upgrades"]}
 ]}
```
Alternative: provide raw Mermaid syntax with `mermaid`.

### kanban-board
Mermaid.js kanban board. Use for mission progression, learning workflow, and project-based modules.
```json
{"type": "kanban-board", "title": "This Week's Learning Workflow",
 "columns": [
   {"id": "todo", "title": "To Learn", "tasks": [
     {"id": "t1", "title": "Read Pod lifecycle", "priority": "High"}
   ]},
   {"id": "doing", "title": "In Practice", "tasks": [
     {"id": "t2", "title": "Run kubectl get pods", "assigned": "Learner"}
   ]},
   {"id": "done", "title": "Mastered", "tasks": [
     {"id": "t3", "title": "Explain rolling updates to a peer"}
   ]}
 ]}
```
Optional: `ticket_base_url` for linked ticket metadata.

### radar-profile
Mermaid.js radar chart (v11.6.0+). Use for skill snapshots, before/after comparisons, and student profile visuals.
```json
{"type": "radar-profile", "title": "Current Skill Profile",
 "chart_title": "Session 4 Competency Snapshot",
 "axes": [
   {"id": "concepts", "label": "Concept Clarity"},
   {"id": "debugging", "label": "Debugging"},
   {"id": "speed", "label": "Execution Speed"},
   {"id": "confidence", "label": "Confidence"}
 ],
 "curves": [
   {"id": "current", "label": "Current", "values": [3, 2, 3, 4]},
   {"id": "target", "label": "Target", "values": [5, 4, 4, 5]}
 ],
 "max": 5,
 "ticks": 5,
 "show_legend": true}
```

Mermaid notes:
- Renderer pins Mermaid at `11.12.2` for deterministic behavior.
- Supported Mermaid-backed components: `concept-map`, `mind-map`, `kanban-board`, `radar-profile`.

---

## AI-Powered Components (conversational — handled by agent in chat)

These are **asked by the agent in conversation** between the explainer and test phases, not rendered into HTML. Use 1-2 per session maximum in the conversational checkpoint. The JSON schemas below document what the agent should ask — they are not passed to `build-lesson.py`.

### explain-back
The student explains a concept in their own words. Based on the Feynman technique — if you can't explain it simply, you don't understand it.
```json
{"type": "explain-back", "title": "Teach It Back",
 "prompt": "Imagine a friend asks: 'Why can't I just use Docker for everything?' Explain in 2-3 sentences why you'd need something like Kubernetes.",
 "hint": "Think about what happens when you have 50 containers and one crashes at 3am.",
 "concept": "container-orchestration",
 "eval_criteria": "Should mention: scale/many containers, automation of recovery, and human limitation at scale"}
```
- The agent asks this question in conversation during the checkpoint (Step 5), not in HTML
- `eval_criteria` guides the agent's real-time evaluation of the student's response
- The agent gives immediate nuanced feedback in the conversation

### debug-challenge
Present broken code, config, or logic. The student finds and explains the bug. Validated by SIGCSE 2025 research — debugging exercises match instructor-crafted quality.
```json
{"type": "debug-challenge", "title": "Find the Bug",
 "language": "yaml",
 "broken_code": "apiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: web\nspec:\n  replicas: three\n  selector:\n    matchLabels:\n      app: web",
 "bug_description": "This Deployment config has an error. Can you spot it?",
 "hint": "Look at the data types carefully.",
 "correct_explanation": "replicas must be an integer (3), not a string (\"three\")",
 "concept": "deployments",
 "difficulty": "beginner"}
```
- Rendered as a code block with the bug, plus a reveal button for the answer
- Student tries to find it first, then checks — the "attempt then verify" pattern

### roleplay
Put the student in a scenario where they must make decisions or respond as a specific role. Powerful for soft skills, incident response, design decisions, ethical dilemmas.
```json
{"type": "roleplay", "title": "Incident Commander",
 "scenario": "It's 2am. PagerDuty wakes you up. The monitoring dashboard shows 3 of your 5 pods are in CrashLoopBackOff. Customer complaints are flooding in. You're the on-call engineer.",
 "prompt": "What's your first move? Write 2-3 steps you'd take, in order.",
 "context": "You have access to kubectl, the monitoring dashboard, and the team Slack channel.",
 "concept": "incident-response",
 "eval_criteria": "Good answers: check logs first (kubectl logs), check events (kubectl describe), communicate in Slack. Red flags: immediately restarting without checking logs, ignoring communication."}
```

### open-reflection
A moment of metacognition. Ask the student to reflect on their learning, connect concepts, or think about application. Best at the end of a session or module.
```json
{"type": "open-reflection", "title": "Think About It",
 "prompt": "What's one thing from today's session that you'd do differently in your current project?",
 "context": "There's no wrong answer here — this is about connecting what you learned to your actual work.",
 "concept": "metacognition"}
```

---

## Real-World Components (bridges to the outside — explainer phase)

These components break the fourth wall — they send the student into the real world to do, explore, or experience something. This is where learning gets memorable.

### real-world-mission
Send the student to a real tool, website, sandbox, or activity. Follow up in the next session.
```json
{"type": "real-world-mission", "title": "Hands-On Mission",
 "mission": "Go to play-with-k8s.com, start a session, and run: kubectl get nodes. Screenshot what you see — we'll discuss it next time.",
 "url": "https://labs.play-with-k8s.com/",
 "context": "This is a free Kubernetes playground — no install needed. Sessions last 4 hours.",
 "followup": "Next session: we'll look at your screenshot and talk about what those nodes actually are.",
 "mission_type": "sandbox"}
```

Mission types (for the agent's reference, not rendered differently):
- `sandbox` — use a live tool or playground
- `observe` — look at something real (a website's network tab, a GitHub repo, a running process)
- `create` — make something (a drawing, a diagram, a short piece of writing)
- `social` — explain a concept to someone, discuss with a peer
- `explore` — browse a resource, find something specific, report back

Examples of adventurous missions:
- "Draw the architecture of your ideal system on paper and photograph it"
- "Open your browser's network tab on your favorite website — count how many requests fire. Surprising?"
- "Find a real Kubernetes outage postmortem on the internet. What went wrong?"
- "Explain today's main concept to someone who doesn't work in tech. What analogy did you use?"
- "Go to GitHub and find a real Dockerfile for a language you know. What do you recognize?"

### recommended-deep-dive
Suggest optional longer-form resources for students who want to go deeper. Not required, never tested on — just curated recommendations from your research.
```json
{"type": "recommended-deep-dive", "title": "Want to Go Deeper?",
 "resources": [
   {"type": "video", "title": "Kubernetes Deconstructed", "url": "https://youtube.com/watch?v=...", "duration": "30 min", "why": "The best visual explanation of the K8s control loop I've found"},
   {"type": "article", "title": "The Children's Illustrated Guide to Kubernetes", "url": "https://...", "why": "Delightfully weird and surprisingly deep"},
   {"type": "book", "title": "Kubernetes Up & Running", "author": "Hightower et al.", "why": "The definitive guide, worth owning"},
   {"type": "tool", "title": "k9s", "url": "https://k9scli.io/", "why": "Terminal UI for Kubernetes — makes kubectl feel ancient"}
 ]}
```

### community-challenge
Pose a challenge the student can take to a community (Stack Overflow, Discord, Reddit, a team Slack). Social learning amplifies retention.
```json
{"type": "community-challenge", "title": "Community Challenge",
 "challenge": "Find someone who uses Kubernetes at work. Ask them: 'What's the one thing you wish you'd known when you started?' Share their answer next session.",
 "context": "If you don't know anyone, try the Kubernetes Slack (slack.k8s.io) — the #kubernetes-novice channel is very welcoming.",
 "followup": "We'll compare their advice to what you've been learning."}
```

---

## Gamification Components

### score-summary
End-of-session score display. Always place last.
```json
{"type": "score-summary", "title": "Session 3 Complete!", "vocab_total": 9,
 "learned": ["How pods get scheduled onto nodes", "What kubelet does", "Resource requests and limits"],
 "next_preview": "In Session 4, we'll look at Deployments in depth...",
 "missions_pending": ["Your sandbox mission: try kubectl get nodes"]}
```

---

## Custom Components

### custom
Pass-through for agent-invented components. Use when no template fits and you have a genuinely good idea for an interaction.
```json
{"type": "custom", "html": "<div>Custom interactive HTML</div>", "js": "function myThing(){...}", "css": ".my-class{color:red}"}
```
Use creatively but not lazily. If a standard component can do the job, prefer it.

---

## Component Selection Quick Reference

| When you want to... | Use |
|---------------------|-----|
| Explain something | `story-card` |
| Introduce vocabulary | `vocab-cards` |
| Test recall | `quiz` |
| Test connections | `matching` |
| Build something step-by-step | `fill-blanks` |
| Show order/process | `sorting-game` or `timeline` |
| Compare two things | `side-by-side` |
| Show relationships | `concept-map` |
| Show hierarchy/prerequisites | `mind-map` |
| Visualize workflow status | `kanban-board` |
| Compare competency dimensions | `radar-profile` |
| Demonstrate behavior | `simulator` |
| Check real understanding | `explain-back` |
| Teach debugging skills | `debug-challenge` |
| Build empathy/decision-making | `roleplay` |
| Encourage metacognition | `open-reflection` |
| Send them to a real tool | `real-world-mission` |
| Suggest further reading | `recommended-deep-dive` |
| Engage social learning | `community-challenge` |
| Show a short video | `video-embed` |
| Celebrate completion | `score-summary` |
| Invent something new | `custom` |
