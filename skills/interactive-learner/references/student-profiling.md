# Student Profiling

## First-Time Setup

When starting a new course with a new student, gather this information **conversationally** (not as a form). This is a chat, not an intake survey.

### Essential (must ask)

1. **Background**: What do they already know about this topic? What adjacent knowledge do they have?
2. **Goal**: Why are they learning this? (job, promotion, hobby, curiosity, deadline, switching careers)
3. **Constraints**: Time per session? (suggest 15-25 min). Any hardware or access limits?

### Important (ask naturally)

4. **Analogies from their world**: What's their day job? Hobbies? Interests? These become your primary teaching tools. A musician understands composition/harmony. A cook understands recipes/timing. A parent understands scheduling/resource management.
5. **Existing tools**: What do they already use? (Docker, Git, VSCode, Figma, Excel, specific languages)
6. **Preferred depth**: Quick practical overview, or deep conceptual understanding?

### Infer from conversation (don't ask directly)

- **Pace**: Fast learner or wants more repetition? (gauge from quiz scores and conversation)
- **Jargon tolerance**: Technical vs plain language? (default to plain, adjust up)
- **Visual vs text**: Do they ask for diagrams, or are they happy with descriptions?
- **Confidence level**: Are they bold and experimental, or cautious and want confirmation?

### Optional (ask if relevant to the topic)

- **Language preference**: For code examples — Python, JavaScript, Go, etc.
- **Real-world access**: Can they install tools? Run terminals? Access playgrounds?
- **Social context**: Are they learning alone, with a team, for a certification?

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
