---
name: interactive-learner
description: "Personal AI tutoring skill that deeply researches any topic, then creates rich, interactive HTML courses with quizzes, simulators, debug challenges, explain-back exercises, real-world missions, and more. Tracks per-concept mastery across sessions with spaced repetition. Use when: (1) the user wants to learn a new topic, (2) the user says 'teach me X' or 'I want to learn X', (3) the user asks for an interactive lesson or course, (4) the user wants to study or review a subject. Works for any topic: technical, conceptual, creative, math, languages."
metadata:
  version: 0.1.0
---

# Interactive Learner

Create deeply researched, engaging, interactive courses on any topic. Lessons open in the browser with a mix of click-based exercises, open-ended challenges, real-world missions, and AI-evaluated responses. Every course is personalized, evidence-based, and a little adventurous.

## Workflow

### New course: Profile → Research → Curriculum → Session → Build → Debrief

#### 1. Profile the student (first time only)

Keep profiling fast and frictionless. The student wants to learn, not fill out forms.

**Rules:**

- **Prefer multiple-choice questions.** They're faster to answer and give you structured data. Use the agent's question tool with concrete options wherever possible.
- **Max 1 open-ended question at a time.** Never dump multiple open questions in one message.
- **Max 3-4 profiling questions total.** Infer the rest from context and conversation.
- **Start teaching quickly.** You can refine the profile during the first session based on how they perform.

**What to gather (in order of priority):**

1. Experience level with this topic (multiple-choice: none / some exposure / use it occasionally / use it daily)
2. Goal (multiple-choice: career / hobby / curiosity / specific task + optional free text)
3. Time per session (multiple-choice: ~10 min / ~20 min / ~30+ min)
4. Background — only if not obvious from context (one open question max, e.g. "What's your day job or main interest?")

Infer (don't ask): learning pace, jargon tolerance, visual vs text preference, analogies from their domain.

See [student-profiling.md](references/student-profiling.md) for the full profiling framework.

Initialize progress:

```bash
uv run .agents/skills/interactive-learner/scripts/progress.py init <course> <name>
```

#### 2. Research the topic thoroughly

**This is critical. Do not skip or rush this step.** Before designing any curriculum, become an expert on the subject.

**Important: Do your research directly.** Use web search, read documentation, and fetch pages yourself. Do NOT delegate research to a background agent — it gets stuck on permission prompts and wastes time.

**Deep research protocol:**

1. **Search for authoritative, recent sources** — prioritize official documentation, peer-reviewed content, respected practitioners, and recent (2024-2026) material
2. **Find the best learning resources that already exist** — outstanding blog posts, interactive tutorials, YouTube channels, open-source tools, practice sandboxes, visualization tools, community forums
3. **Identify the conceptual structure** — what are the foundational concepts? What depends on what? What are the common misconceptions? What's the optimal learning order?
4. **Discover the "aha moments"** — what analogies, visualizations, or exercises make this topic click for people? What do the best teachers do differently?
5. **Collect real-world examples** — case studies, war stories, practical applications that make abstract concepts tangible
6. **Find hands-on resources** — playgrounds, sandboxes, tools the student can actually use during the course

**Save research notes** to a file the student can reference later:

```bash
# Write research to a markdown file alongside the course
# Include: key sources, recommended deep-dives, practice resources, community links
```

**Source priorities** (in order):

1. Official documentation and specs
2. Peer-reviewed research / reputable educational content
3. Respected practitioners and educators (conference talks, well-known blogs)
4. Community-vetted resources (highly-rated tutorials, curated awesome-lists)
5. Interactive tools and sandboxes

#### 3. Design the curriculum

Based on research, plan the full course:

- 8-12 sessions for a standard course (3-5 for quick intro, 12-20 for deep dive)
- Define learning objectives per session — what will the student be able to DO after each one?
- Map concept dependencies — what must come before what?
- Plan review touchpoints — which earlier concepts get revisited where?
- Identify sessions where real-world missions, external tools, or deeper exploration fit naturally
- Max 6 new vocabulary terms per session, each with a bridging analogy

Save the curriculum and show it to the student as an interactive dashboard:

1. Write a curriculum JSON file (array of session objects):
   ```json
   [
     {
       "session_number": 1,
       "title": "How Bash Actually Works",
       "description": "The mental model that changes everything",
       "objectives": ["Explain what a shell does", "Break down command syntax"],
       "concepts": ["shell-mental-model", "commands-and-arguments"],
       "estimated_minutes": 20
     }
   ]
   ```
2. Save it to the course progress:
   ```bash
   uv run .agents/skills/interactive-learner/scripts/progress.py set-curriculum <course> <curriculum.json>
   ```
3. Build and open the dashboard so the student can see the full plan:
   ```bash
   uv run .agents/skills/interactive-learner/scripts/build-dashboard.py --open
   ```

Let the student react, reprioritize, skip things they know. This is collaborative.

See [course-design-guide.md](references/course-design-guide.md) for topic-type → component mapping and session patterns.

#### 4. Generate a lesson JSON for the current session

Build a lesson config using the component catalog:

- See [component-catalog.md](references/component-catalog.md) for all components and their JSON schemas
- See [sharp-edges.md](references/sharp-edges.md) for anti-patterns to avoid
- Mix component types — no two consecutive sections of the same type
- Include at least one moment of surprise, delight, or creative challenge per session
- Keep JSON concise but rich: ~80-150 lines depending on session complexity

#### 5. Build and open the lesson

```bash
uv run .agents/skills/interactive-learner/scripts/build-lesson.py <lesson.json> --output <path>/lesson.html --open
```

#### 6. Debrief after the session

After the student completes the lesson:

- Update progress with scores AND concept mastery:
  ```bash
  uv run .agents/skills/interactive-learner/scripts/progress.py update <course> --session N --score S --max M --concepts '{"pod-basics": 0.9, "deployments": 0.6}'
  ```
- Discuss what they found hard or interesting
- If they did an explain-back or open-answer: evaluate their response, give specific feedback, note misunderstandings for the next session
- If they had a real-world mission: ask how it went, what they discovered
- Adjust the next session based on everything you learned

### Returning student: Review → Adapt → Build next session

```bash
uv run .agents/skills/interactive-learner/scripts/progress.py show
```

Check:

- Concept mastery levels — which concepts need review? (below 0.7 = needs reinforcement)
- Time since last session — longer gap = more review needed
- Recent scores — adjust difficulty
- Open questions or missions from last session — follow up on these
- Achievements earned — acknowledge naturally

Generate the next session, weaving in review of weak concepts using varied component types (not just repeating the same quiz).

### Generate review session (when needed)

When concepts are fading or it's been a while:

```bash
uv run .agents/skills/interactive-learner/scripts/progress.py review <course>
```

This outputs concepts due for review. Build a review session that mixes these concepts into fresh contexts and varied exercise types.

### View student dashboard

```bash
uv run .agents/skills/interactive-learner/scripts/build-dashboard.py --open
```

Options: `--progress <path>` (custom progress file), `--output <path>` (custom output path).

## Lesson JSON Structure

```json
{
  "course_name": "Kubernetes",
  "title": "Why Does Kubernetes Exist?",
  "subtitle": "The problem before the solution",
  "session": 1,
  "estimated_minutes": 20,
  "xp_start": 0,
  "concepts": ["container-orchestration", "scaling-problem", "self-healing"],
  "theme_css": "",
  "sections": [
    {
      "type": "story-card",
      "variant": "blue",
      "label": "The Problem",
      "content": "<p>Imagine you're running 50 containers...</p>"
    },
    {
      "type": "quiz",
      "questions": [
        {
          "question": "Before you learn anything: what do you THINK happens when a container crashes?",
          "options": ["..."],
          "correct": 1,
          "feedback_correct": "...",
          "feedback_wrong": "..."
        }
      ]
    },
    { "type": "vocab-cards", "terms": [{ "term": "Pod", "icon": "🫛", "definition": "...", "analogy": "..." }] },
    {
      "type": "explain-back",
      "prompt": "In one sentence, explain why you can't just use Docker alone for 50 containers.",
      "hint": "Think about what happens when things go wrong at scale.",
      "concept": "container-orchestration"
    },
    {
      "type": "real-world-mission",
      "mission": "Open play-with-k8s.com and run: kubectl get nodes. How many nodes do you see?",
      "url": "https://labs.play-with-k8s.com/",
      "context": "This is a free Kubernetes playground — no install needed.",
      "followup": "We'll discuss what you found at the start of next session."
    },
    {
      "type": "score-summary",
      "learned": ["Why container orchestration exists"],
      "next_preview": "Next: what Kubernetes actually does about these problems."
    }
  ]
}
```

## Available Components

### Core (click-based, scored)

`quiz` `matching` `fill-blanks` `sorting-game` `simulator`

### Content (explanatory)

`story-card` `vocab-cards` `side-by-side` `video-embed` `timeline` `concept-map`

### Mermaid-native visuals

`mind-map` `kanban-board` `radar-profile`

### AI-powered (open-ended, evaluated by agent)

`explain-back` `debug-challenge` `roleplay` `open-reflection`

### Real-world (bridges to the outside)

`real-world-mission` `recommended-deep-dive` `community-challenge`

### Gamification

`score-summary`

### Escape hatch

`custom` — when no template fits, invent something new.

Full JSON schemas and usage guidance: [component-catalog.md](references/component-catalog.md)

## Finding Videos

```bash
uv run .agents/skills/interactive-learner/scripts/find-videos.py "topic for beginners"
```

Max 2 embedded videos per lesson. But you CAN recommend additional videos/resources via `recommended-deep-dive` components — these are optional extras, not required viewing.

## Core Rules

1. **Research first.** Never teach from assumptions. Find authoritative, recent sources.
2. **Bridge from known knowledge.** Read the student profile. Connect every new concept to something they already understand.
3. **Challenge before explanation** (default). Let the student attempt or predict before you explain. Discovery beats lecture.
4. **Mostly click-based.** The majority of interactions should be click/drag/select. But sprinkle in open-ended moments — they're powerful when used intentionally.
5. **Open answers are a tool, not a crutch.** Use explain-back, roleplay, or open-reflection for 1-3 moments per session where real thinking matters. The agent evaluates these in the debrief. Never use them as filler.
6. **Max 6 new terms per session.** Each needs an analogy bridging to what the student knows.
7. **50% practice, 30% content, 20% assessment** — but treat this as a guideline, not a straitjacket. Some sessions are exploration-heavy, some are drill-heavy.
8. **Vary components.** No two consecutive sections should be the same type.
9. **Always end with score-summary.**
10. **Be adventurous.** Send students to real websites, sandboxes, and tools. Recommend books, talks, and articles. Ask them to draw something and share it. Suggest they explain a concept to a friend. The lesson HTML is the core, but learning extends beyond it.
11. **Achievements are dynamic.** Don't use a fixed list. Generate achievements that match the specific course, topic, and student milestones. See [gamification.md](references/gamification.md).
12. **Every interaction earns data.** Track concept mastery, not just session scores. Feed this into future sessions.

## Anti-patterns

See [sharp-edges.md](references/sharp-edges.md) — updated with guidance on when open answers help vs hurt, and new anti-patterns around research shortcuts and stale content.

## Gamification

See [gamification.md](references/gamification.md) — dynamic achievements, XP, streaks, and the memory garden concept.
