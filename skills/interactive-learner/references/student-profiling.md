# Student Profiling

## First-Time Setup

Keep profiling fast and frictionless. The student came to learn, not to answer an intake survey. Get the minimum info needed to personalize, then start teaching. Refine as you go.

### Interaction rules

- **Prefer multiple-choice questions.** Use the agent's question tool with concrete options. Multiple-choice is faster to answer and gives structured signal.
- **Max 1 open-ended question at a time.** Never send multiple open questions in one message.
- **Max 3-4 profiling questions total** before starting the first session.
- **Start teaching quickly.** You'll learn more from how they perform in session 1 than from a pre-interview.

### What to ask (in priority order)

1. **Experience level** (multiple-choice): none / some exposure / use it occasionally / use it daily
2. **Goal** (multiple-choice + optional free text): career / hobby / curiosity / specific task — if they pick "specific task", one follow-up to clarify
3. **Time per session** (multiple-choice): ~10 min / ~20 min / ~30+ min
4. **Background** (open, only if not obvious from context): "What's your day job or main interest?" — this gives you analogy material

### Infer from context and performance (don't ask)

- **Pace**: Gauge from quiz scores and conversation speed
- **Jargon tolerance**: Default to plain language, adjust up if they use technical terms
- **Visual vs text**: Observe whether they ask for diagrams or examples
- **Confidence level**: Bold/experimental vs cautious — adjust scaffolding accordingly
- **Analogies from their world**: Derive from their background answer and topic choice
- **Existing tools**: Infer from topic choice and experience level, ask only if critical for examples

### Optional (ask during session, not upfront)

- **Language preference**: For code examples — ask when you first need to write code, not before
- **Real-world access**: Ask when you plan a hands-on mission, not during profiling
- **Preferred depth**: Infer from goal and experience level

## Returning Student

When a student returns for a new session, read progress:
```bash
uv run .agents/skills/interactive-learner/scripts/progress.py show
uv run .agents/skills/interactive-learner/scripts/progress.py show --concepts
uv run .agents/skills/interactive-learner/scripts/progress.py review <course>
```

Check:
- **Concept mastery** — which concepts are strong (≥0.8), moderate (0.5-0.7), or weak (<0.5)?
- **Concepts due for review** — FSRS says these are fading. Weave them into the next session.
- **Time since last session** — longer gap = more review needed, start gently
- **Recent scores** — adjust difficulty accordingly
- **Pending missions** — follow up! Ask how it went. This is critical.
- **Open responses from last session** — if they did an explain-back or roleplay, you should have noted areas for feedback
- **Streak** — acknowledge naturally if active, never guilt if broken
- **Achievements** — mention recent ones briefly, especially if they unlocked something cool

## Profile Storage

Initialize a profile:
```bash
uv run .agents/skills/interactive-learner/scripts/progress.py init <course-name> <student-name>
```

Update after each session:
```bash
uv run .agents/skills/interactive-learner/scripts/progress.py update <course-name> --session N --score S --max M --concepts '{"concept-id": 0.8}'
```

Grant achievements:
```bash
uv run .agents/skills/interactive-learner/scripts/progress.py achieve <course> <id> <icon> <name> <description>
```

Log missions:
```bash
uv run .agents/skills/interactive-learner/scripts/progress.py mission <course> "description of the mission"
uv run .agents/skills/interactive-learner/scripts/progress.py mission-complete <course> <index>
```

## Adapting Content Based on Profile

| Signal | Adaptation |
|--------|-----------|
| Marketing background | Business analogies, campaign metaphors |
| Developer background | Code examples, system design analogies |
| Scores 100% × 2 | Skip basic exercises, add advanced challenges, more open-ended |
| Scores below 60% | Add more examples, slower pace, review previous material |
| Knows Docker | Bridge container concepts, skip "what is a container" |
| Knows Python | Use Python for code examples over other languages |
| Limited install access | Use web-based playgrounds, sandbox missions |
| Time-constrained (10 min) | Shorter sessions, fewer components, skip deep-dives |
| Concepts fading | Weave review into new content, vary the modality |
| Completed missions | Follow up — their experience is content for the next session |
| Bold/experimental personality | More open-ended challenges, harder debug exercises, surprise missions |
| Cautious personality | More scaffolding, more feedback, confirm understanding before advancing |

## The Debrief (After Each Session)

The debrief conversation is where the deepest learning happens. After the student finishes the HTML lesson:

1. **Ask about their experience** — What was hard? What clicked? What surprised them?
2. **Evaluate open responses** — Read their explain-back, roleplay, or reflection answers. Give specific, constructive feedback. Identify misconceptions.
3. **Follow up on missions** — If they did a real-world mission, ask what they found. Use their experience as a teaching moment.
4. **Note insights for next session** — What needs reinforcement? What can be skipped? What sparked their curiosity?
5. **Update progress** — Score, concept mastery, achievements, mission status.
6. **Preview next session** — Give them something to look forward to.

The debrief turns a one-directional lesson into a two-way learning relationship.
