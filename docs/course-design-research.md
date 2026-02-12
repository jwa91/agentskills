# How to Create a Great Course — Research Summary

> Comprehensive research on online learning, digital education, and course design best practices (2025-2026 sources). Organized by topic with actionable insights for building the interactive-learner skill.

---

## 1. Evidence-Based Learning Principles

The strongest, most-replicated findings in learning science. These are the non-negotiables.

### Active Recall (Retrieval Practice)

**What it is:** Effortful recall of information from memory (self-testing), rather than passive re-reading or re-watching.

**Why it works:** Retrieval creates and strengthens memory pathways. Recent research (Nature Reviews Psychology, 2022; Karpicke & O'Day, 2024) shows it works via *prediction error* — when you try to recall and get feedback, the mismatch between your guess and the answer drives deeper encoding.

**Key findings:**
- Retrieval practice produces stronger, longer-lasting memory than any form of passive review
- Feedback after retrieval is essential — without it, the benefits collapse
- Works across all ages, domains, and settings (lab and classroom)
- Even failed retrieval attempts improve learning when followed by feedback

**Actionable for the skill:**
- Every session must include retrieval-based exercises (quiz, fill-blanks, matching) — not just content presentation
- Always provide explanatory feedback on wrong answers (not just "incorrect")
- The current 50% practice / 30% content / 20% assessment split is well-supported by research — keep it
- Consider adding "retrieval warm-ups" at the start of sessions that test previous material

### Spaced Repetition (Distributed Practice)

**What it is:** Spreading practice over time rather than massing it in one session.

**Why it works:** Spacing forces retrieval from increasingly weak memory traces, which strengthens long-term retention. Optimal intervals depend on the retention goal, but the effect is remarkably robust.

**Key findings:**
- One of the two strongest effects in all of learning science (alongside retrieval practice)
- Even crude spacing (e.g., reviewing yesterday's material today) dramatically outperforms no spacing
- Expanding intervals (1 day → 3 days → 7 days → 30 days) optimize retention for long-term goals

**Actionable for the skill:**
- The progress system already tracks sessions, but could add spaced review scheduling
- Each session's opening recap is a lightweight spacing mechanism — formalize it
- Consider auto-generating "review sessions" that pull items from past lessons at calculated intervals
- The dashboard could show "due for review" indicators per course

### Interleaving

**What it is:** Mixing different problem types or categories during practice, rather than practicing one type at a time (blocked practice).

**Why it works:** Interleaving forces learners to discriminate between problem types and choose the correct strategy — it builds the *when to use what* skill that transfer requires.

**Key findings:**
- Particularly effective for complex skills where choosing the right approach matters
- Often outperforms blocked practice for long-term retention and transfer
- Feels harder during practice (learners prefer blocking) but produces better results
- Most effective when the interleaved categories share surface features but differ in deep structure

**Actionable for the skill:**
- Don't group all quiz questions on the same sub-topic — mix topics within exercises
- The "vary components" rule already supports this; reinforce that varying *content type within exercises* matters too
- Later sessions should include problems from earlier sessions mixed with new material
- Boss challenges at module boundaries should interleave concepts from multiple sessions

### Elaboration

**What it is:** Generating explanations, connections, or examples that go beyond the presented material.

**Why it works:** Creates more distinctive, organized memory traces with richer retrieval cues. The act of connecting new information to existing knowledge creates multiple access paths.

**Key findings:**
- "Why does this make sense?" and "How does this relate to X?" prompts improve retention
- Self-explanation (explaining to yourself) is more effective than re-reading by a large margin
- Works best when tied to core principles rather than surface features

**Actionable for the skill:**
- Analogy-based vocab cards already leverage elaboration — keep the "analogy" field required
- Add "how is this similar to / different from X?" comparison prompts
- The bridging principle (connecting to student's existing knowledge) is a form of elaboration — it's well-supported
- Consider a "teach-back" component where the student must explain a concept by choosing the correct explanation

### Dual Coding

**What it is:** Combining verbal/text information with relevant visual representations.

**Why it works:** Creates two complementary memory traces (verbal + visual) that can be independently retrieved, improving recall.

**Key findings:**
- Concrete examples paired with abstract ideas enhance encoding
- The visual must be *relevant* and *integrated* — decorative images actually hurt learning (Mayer's coherence principle)
- Diagrams, concept maps, timelines, and annotated images are effective dual coding formats

**Actionable for the skill:**
- The concept-map, timeline, and side-by-side components are strong dual-coding tools
- Vocab cards could benefit from icons/emojis (already present) — ensure they're semantically meaningful, not decorative
- Story cards that explain processes should have accompanying diagrams where possible
- Avoid purely decorative visuals — every image should carry information

---

## 2. Course Design Frameworks

### ADDIE (Analyze, Design, Develop, Implement, Evaluate)

The most widely used instructional design model. Iterative, not linear.

| Phase | What Happens | For the Skill |
|-------|-------------|---------------|
| **Analyze** | Define learner needs, context, constraints | Student profiling step — already implemented |
| **Design** | Set objectives, choose assessments, plan sequence | Curriculum design step — map sessions to objectives |
| **Develop** | Build content and activities | Lesson JSON generation |
| **Implement** | Deliver to learners | `build-lesson.py` → browser |
| **Evaluate** | Assess effectiveness, iterate | Progress tracking + score analysis |

**Key insight:** The skill's existing workflow (Profile → Curriculum → Session → Build → Score) maps cleanly to ADDIE. This is good — it means the workflow is pedagogically sound.

### Backward Design (Wiggins & McTighe)

**The core idea:** Start with desired outcomes, then design assessments, then plan instruction — in that order.

1. **Identify desired results** — What should the learner understand and be able to do?
2. **Determine acceptable evidence** — How will you know they understand? What assessments prove it?
3. **Plan learning experiences** — What activities and content prepare them for those assessments?

**Why it matters:** Many courses fail because they start with "what content do I have?" instead of "what should the learner be able to do?" This leads to content-heavy, assessment-light courses.

**Actionable for the skill:**
- The curriculum design step should explicitly require: (1) end-of-course learning objectives, (2) how each session will assess those objectives, (3) then the activities
- Each session JSON should have a `learning_objectives` field that links to the assessment components
- The current course-design-guide mentions session structure but could formalize the backward design sequence

### Universal Design for Learning (UDL)

**The three principles:**
1. Multiple means of *representation* (present information in various formats)
2. Multiple means of *action and expression* (let learners demonstrate knowledge in different ways)
3. Multiple means of *engagement* (tap into varied interests and motivations)

**Actionable for the skill:**
- The component variety rule already supports multiple representation — good
- The custom component type enables flexible expression — good
- Consider offering learners choice in some exercises (e.g., "try the matching game OR the sorting game")

---

## 3. What Makes Online Courses Effective vs. Ineffective

### The Effective Course (evidence-based markers)

Research from Frontiers in Psychology (2025) and a meta-review in Journal of Technology and Education (2024) identified consistent factors:

1. **Clear structure and signposting** — Learners know where they are, what's next, and what's expected
2. **High-quality interaction** — Not just content consumption; frequent, meaningful back-and-forth
3. **Timely, specific feedback** — Not just "correct/incorrect" but explanatory
4. **Authentic/challenging activities** — Tasks that mirror real use of the knowledge
5. **Instructor/tutor presence** — Feeling that someone is guiding you (not just clicking through slides)
6. **Self-regulation scaffolds** — Explicit help with goal-setting, time management, and study strategies

### The Ineffective Course (common failure modes)

1. **Lecture-dump format** — Simply recording lectures and putting them online
2. **One-size-fits-all** — No adaptation to learner level or pace
3. **Low interaction** — Passive video watching with a quiz at the end
4. **Weak scaffolding** — Less-prepared students flounder and drop out
5. **No social connection** — Isolation kills motivation

### Critical Stat

Typical online course completion rates: **5-15%**. Well-designed courses: **~85%**. The difference is entirely design, not content quality.

**Actionable for the skill:**
- The skill already addresses many "effective" markers (interaction, feedback, structure)
- The "tutor presence" factor is interesting — the agent *is* the tutor. Conversational tone in story cards matters
- Consider adding explicit self-regulation prompts ("You've covered 3 of 5 sections — take a break if needed")
- The session preview and progress tracking serve as signposting
- The score-summary component serves as both feedback and motivation

---

## 4. Engagement Techniques That Actually Work

Research distinguishes between *genuine engagement* (cognitive, emotional, social) and *surface engagement* (clicking buttons, watching counters tick up).

### What Works (evidence from Columbia CCRC, 2025; multiple systematic reviews)

| Technique | Why It Works | Skill Implementation |
|-----------|-------------|---------------------|
| **Frequent low-stakes practice** | Reduces anxiety, increases attempts, drives retrieval | Quiz, matching, fill-blanks — already strong |
| **Meaningful instructor presence** | Humans need to feel guided, not abandoned | Agent's conversational framing of lessons |
| **Real-world connection** | "Why does this matter to me?" drives motivation | Bridging principle + motivational story cards |
| **Student-generated artifacts** | Creating something concrete increases ownership | Consider: "build a config" or "design a solution" components |
| **Peer-to-peer interaction** | Social accountability and collaborative sense-making | Outside current scope (single learner) but worth noting |
| **Scaffolded self-direction** | Goal-setting and reflection build autonomy | Session previews, progress tracking, pacing rules |
| **Challenge → reveal (productive failure)** | Attempting before being taught improves learning | Pattern B (Discovery) in course-design-guide |

### What Doesn't Work (or backfires)

| Technique | Why It Fails |
|-----------|-------------|
| **Points/badges without meaning** | External rewards undermine intrinsic motivation when overused |
| **Leaderboards in learning contexts** | Anxiety-inducing for most learners; benefits a small competitive minority |
| **Streaks as primary motivator** | Creates guilt and "streak anxiety" — learning becomes about the number, not understanding |
| **Entertainment > education** | Fun activities that don't drive learning create an illusion of progress |
| **Passive video marathons** | Engagement drops sharply after 6-10 minutes of passive viewing |

**Actionable for the skill:**
- The gamification system (XP, streak, achievements) should be *secondary* to learning signals
- Reframe streaks as "consistency" rather than an unbreakable chain — missing a day shouldn't feel punitive
- The most powerful engagement tool is *appropriate challenge level* — too easy is boring, too hard is frustrating
- Pattern B (Discovery/challenge-first) is particularly well-supported — use it more often
- Video segments should be 2-8 minutes max, with activity bookending (confirmed by the sharp-edges guide)

---

## 5. Microlearning vs. Deep Learning — When to Use Each

### Microlearning (bite-sized, 3-15 minutes)

**Best for:**
- Specific, narrow learning goals (one concept, one procedure)
- Spaced retrieval and review sessions
- Just-in-time / on-the-job learning
- Building daily habits (Duolingo model)
- Mobile-first delivery
- Vocabulary acquisition and factual knowledge

**Not good for:**
- Complex conceptual understanding that requires building mental models
- Skills that require sustained practice and deep focus
- Topics where context and connection between ideas is essential

### Deep Learning Sessions (25-60 minutes)

**Best for:**
- Building mental models and conceptual frameworks
- Complex problem-solving skills
- Transfer and application across contexts
- Synthesis of multiple related concepts
- Project-based and authentic tasks

### The Hybrid Approach (best of both)

Research (Heliyon, 2024; IEEE, 2024) strongly supports combining both:
- Use microlearning for initial exposure, vocabulary, and spaced review
- Use deeper sessions for conceptual understanding, complex practice, and synthesis
- Use AI to sequence and personalize the mix

**Actionable for the skill:**
- Current sessions target 15-25 minutes — this is a good sweet spot (long micro / short deep)
- Consider adding a "quick review" session type (5-8 minutes) for spaced repetition
- For complex topics, allow multi-session deep dives with a single concept thread
- The course length guidelines (1-3, 8-12, 12-20 sessions) already support this range
- Each session should be completable in one sitting — don't leave learners mid-concept

---

## 6. Assessment Design

### The Core Distinction

| | Formative Assessment | Summative Assessment |
|---|---|---|
| **Purpose** | Guide learning (diagnostic) | Evaluate learning (grading) |
| **Stakes** | Low — mistakes are learning opportunities | Higher — demonstrates mastery |
| **Timing** | Frequent, throughout learning | At milestones or end |
| **Feedback** | Immediate, detailed, actionable | Delayed, evaluative |
| **Examples** | Practice quizzes, think-pair-share, exit tickets | Final exams, portfolios, capstone projects |

### Testing Understanding, Not Memorization

Research (MIT Digital Learning Toolkit, 2025; Open University, 2025) provides clear guidance:

**Recall questions (weak):**
- "What is a Pod in Kubernetes?" → Tests vocabulary recall
- "True or False: React uses a virtual DOM" → Tests recognition

**Understanding questions (strong):**
- "A developer's container keeps crashing. What's the most likely reason a Pod restart count is increasing?" → Tests application
- "Given this component tree, which component should hold the state? Why?" → Tests analysis
- "You need to make 3 services talk to each other. Design the architecture." → Tests synthesis

**Bloom's Taxonomy alignment (from lower to higher):**
1. Remember → Avoid over-testing here
2. Understand → Good baseline
3. Apply → Strong target for most courses
4. Analyze → Excellent for intermediate learners
5. Evaluate → Good for advanced content
6. Create → Best for capstone/project work

**Actionable for the skill:**
- The sharp-edges guide already flags "teaching to the test" and "trivial questions" — good
- Formalize quiz question quality: every question should require at minimum *understanding* level
- Use "what would happen if..." and "which approach would you choose for..." phrasing
- Wrong answer options should be *plausible* — they should represent common misconceptions
- Add feedback that explains *why* wrong answers are wrong, not just *that* they're wrong
- Consider adding "boss challenges" that test transfer (applying concepts to novel situations)
- The score-summary component already serves as formative feedback — ensure it's actionable ("You struggled with X — review this concept")

---

## 7. Personalization and Adaptive Learning

### What Research Shows (2025 systematic reviews covering 125-142 studies)

- AI-driven personalization improves academic performance in ~59% of studied implementations
- Engagement improvement reported in ~36% of cases
- The most effective approaches combine:
  - **Supervised models** for classifying learner level and predicting performance
  - **Reinforcement learning** for dynamic content sequencing
  - **Multimodal analytics** for understanding learner state

### What Actually Works at Individual Learner Scale

1. **Prerequisite-aware sequencing** — Don't teach B until A is mastered
2. **Difficulty adaptation** — Adjust challenge level based on performance
3. **Pacing flexibility** — Let fast learners skip, give struggling learners more practice
4. **Example customization** — Use analogies from the learner's domain
5. **Review scheduling** — Space repetition based on individual retention curves

### Challenges

- Model interpretability (learner should understand why they're seeing certain content)
- Privacy (tracking creates data obligations)
- Over-personalization (can create filter bubbles — learners need to be challenged, not just comfortable)

**Actionable for the skill:**
- The student profiling step enables personalization from session 1
- The pacing rules (accelerate if scoring 100%, decelerate if below 60%) are a simple adaptive mechanism
- The bridging principle (connect to what they know) is personalization at the content level
- Consider adding: difficulty variants for quiz questions (easy/medium/hard, selected based on performance)
- The progress system could inform curriculum adjustments mid-course
- The agent has a unique advantage: it can *generate* personalized content on-the-fly, unlike static course platforms

---

## 8. The Role of AI in Modern Course Design

### Current State (2025-2026)

AI is transforming course design in four areas:

1. **Content generation** — AI generates draft lessons, quiz questions, explanations, and examples. Human review remains essential (Brilliant.org's approach: "hand-crafted, machine-made")
2. **Personalization engines** — AI adapts content sequencing, difficulty, and pacing to individual learners
3. **Assessment innovation** — AI enables "AI-resilient" assessments: process documentation, scenario-based work, portfolios with oral checkpoints
4. **Tutoring and feedback** — AI provides real-time, personalized feedback at scale (Khan Academy's Khanmigo model)

### What's Working

- AI as *content creation accelerator* for human designers (Brilliant: AI generates problem variants, humans curate)
- AI as *personalized tutor* alongside structured curriculum (Khan Academy: Khanmigo assists but doesn't replace the course structure)
- AI as *adaptive sequencer* (Duolingo: ML algorithms determine what to practice next)

### What's Not Working

- AI as *replacement for instructional design* — auto-generated courses without pedagogical expertise
- AI without quality control — "almost right" content that misleads learners (Brilliant's evals blog post is excellent on this)
- AI tutoring without guardrails — giving answers instead of guiding discovery

### Key Design Stat

One AI-based curriculum model reported: 89.72% course completion, 91.44% retention, 4.98% dropout (MDPI, 2025). Compare to the typical 5-15% completion rate.

**Actionable for the skill:**
- The skill's architecture (AI agent generates lesson JSON from templates) is exactly the "hand-crafted, machine-made" model that works best
- Quality control matters: the component catalog and sharp-edges guide serve as guardrails
- The agent should guide discovery, not just present answers — Pattern B (challenge-first) embodies this
- Consider adding an "evals" step: after building a lesson, verify questions have correct answers, options are plausible, and difficulty is appropriate

---

## 9. Common Mistakes in Course Creation

### The Top 10 (synthesized from multiple sources)

| # | Mistake | Why It's Tempting | Fix |
|---|---------|-------------------|-----|
| 1 | **Content-first design** | "I know a lot about this topic" | Start with learning objectives, then assessments, then content (backward design) |
| 2 | **Information overload** | "They need to know all of this" | Ruthlessly prioritize. One core concept per session + 2-3 supporting ideas |
| 3 | **Passive delivery** | "I'll just explain it clearly" | 50%+ of time should be active practice |
| 4 | **No clear objectives** | "It's obvious what they'll learn" | Write explicit, measurable objectives for every session |
| 5 | **Weak assessments** | "A quiz at the end is fine" | Frequent formative assessment with specific feedback |
| 6 | **No learner analysis** | "Everyone starts at the same place" | Profile the learner first. Adapt to their level and background |
| 7 | **Ignoring mobile/accessibility** | "It works on my screen" | Test on multiple devices. Ensure WCAG basics |
| 8 | **Skipping pilot testing** | "It's ready to ship" | Test with real learners. Collect completion data. Iterate |
| 9 | **No spacing/review** | "We covered that in session 2" | Build cumulative review into later sessions |
| 10 | **Gamification over pedagogy** | "Make it fun and they'll learn" | Fun without learning is entertainment. Learning without fun is a textbook. Balance both |

**How the skill currently addresses these:**
- Mistakes 1, 3, 4, 6: Addressed by the workflow (Profile → Curriculum → Session) and course-design-guide
- Mistakes 2, 8, 9: Addressed by sharp-edges (jargon avalanche, firehose) and pacing rules
- Mistakes 5, 10: Addressed by feedback requirements and the 50/30/20 split
- Mistakes 7: Partially addressed (HTML output is responsive, but no formal accessibility checks)
- Mistakes 8, 9: Room for improvement (no formal pilot testing or spaced review mechanism)

---

## 10. What Great Platforms Do Well

### Duolingo — Habit Engine + Learning Science

**The Duolingo Method (5 principles):**
1. Learn by doing (interactive from the first second)
2. AI-driven personalization (adaptive difficulty and review scheduling)
3. Focus on core content (ruthless prioritization)
4. Motivate learners (progress visibility, social features)
5. Entertain and delight (personality, surprise, humor)

**What they do exceptionally well:**
- **Session brevity:** 3-10 minute sessions make starting easy (zero barrier)
- **Active from the first tap:** No passive introduction. You're doing exercises immediately
- **Spaced repetition engine:** ML algorithms schedule review of weak items automatically
- **Progress granularity:** XP, streaks, leagues, levels create many small wins
- **Data-driven iteration:** Every change is A/B tested against learning outcomes

**What to learn from:**
- The power of making sessions *short enough to start without thinking*
- Active recall from the very first interaction
- Review scheduling based on individual performance

**What to be cautious about:**
- Streak anxiety and social pressure can become toxic
- Gamification can overshadow learning (users optimizing for XP, not understanding)
- Shallow depth — good for vocabulary, weaker for complex skills

### Khan Academy — Mastery + Tutor Presence

**What they do exceptionally well:**
- **Mastery-based progression:** Can't advance until you demonstrate understanding
- **Explanation quality:** Clear, conversational, patient explanations
- **Khanmigo (AI tutor):** Guides discovery through Socratic questioning rather than giving answers
- **Classroom integration:** Works for both self-learners and teacher-led classrooms
- **Scored highest in user satisfaction** in 2025 UX comparative study

**What to learn from:**
- Mastery gating is powerful: don't let learners advance past concepts they haven't mastered
- Conversational, patient tone matters enormously
- The Socratic method (asking guiding questions) is more effective than direct instruction

### Brilliant.org — Interactive Problem-Solving

**What they do exceptionally well:**
- **"Feel the concept" approach:** Interactive explorations that build intuition before formalism
- **Tactile learning games:** Not just clicking answers — manipulating, exploring, discovering
- **Massive problem banks:** ~1,000+ calibrated problems per course for genuine mastery
- **Careful difficulty curves:** Each concept has a gradual ramp with scaffolding removal
- **AI for scale, humans for design:** AI generates problem variants; humans design the pedagogy

**What to learn from:**
- Exploration before explanation is powerful (matches Pattern B: Discovery)
- Interactive simulations build deeper understanding than any amount of reading
- Problem variety matters — same concept, many different contexts = transfer
- Quality control on AI-generated content is essential (their evals framework)

### Coursera — Career-Aligned, Credential-Driven

**What they do exceptionally well:**
- **Career alignment:** 86% of learners motivated by career goals; courses connect to outcomes
- **Measurable impact:** 91% positive career outcomes, 46% salary increases from micro-credentials
- **University/industry partnerships:** Content credibility through institutional backing
- **Structured programs:** Clear pathways from individual courses to specializations to degrees

**What to learn from:**
- Connecting learning to real-world goals drives completion
- "What will I be able to DO after this?" is the most powerful motivator
- Structured progression (course → specialization → credential) creates long-term engagement

---

## Synthesis: Key Principles for the Interactive Learner Skill

### What the Skill Already Does Well (keep these)

1. **Profile-first design** — Personalization from the start
2. **Click-based interactions** — Active recall, low friction
3. **50/30/20 split** — Research-supported content:practice:assessment ratio
4. **Component variety** — Dual coding, interleaving of modalities
5. **Bridging principle** — Elaboration through connection to prior knowledge
6. **Anti-pattern documentation** — Explicit guardrails against common mistakes
7. **Explanatory feedback** — Not just correct/incorrect
8. **Session brevity** — 15-25 minutes avoids cognitive overload

### Highest-Impact Improvements to Consider

1. **Spaced repetition engine** — Auto-generate review sessions that pull weak items from past lessons at optimal intervals. This is the single highest-ROI improvement based on learning science.

2. **Challenge-first (Pattern B) as default** — Research on productive failure and the testing effect strongly supports presenting challenges before explanations. Make discovery/challenge-first the primary session pattern.

3. **Mastery gating** — Don't advance to the next session until the current one reaches a threshold score. Khan Academy's most effective feature.

4. **Richer difficulty adaptation** — Go beyond the binary accelerate/decelerate. Offer difficulty variants within exercises. Track per-concept mastery, not just per-session scores.

5. **Learning objectives in the JSON** — Add explicit `learning_objectives` to each lesson. Map every exercise to an objective. This enables backward design verification.

6. **Boss challenges with interleaving** — End-of-module challenges that mix concepts from multiple sessions, requiring transfer and discrimination.

7. **Metacognitive prompts** — Add brief self-regulation moments: "How confident are you?" before a quiz, "What was the most confusing part?" after a session. Research shows these improve learning outcomes.

8. **Quick review sessions** — A 5-minute session type optimized for spaced retrieval. Just exercises, no new content. Pull from the weakest items in the progress data.

### Cognitive Load Checklist (from Mayer's Multimedia Learning)

Apply these when generating lesson content:

- [ ] **Coherence:** Remove decorative content that doesn't support learning
- [ ] **Signaling:** Highlight key information with visual cues
- [ ] **Spatial contiguity:** Place labels near their corresponding visuals
- [ ] **Segmenting:** Break complex content into learner-paced segments
- [ ] **Pre-training:** Introduce key terms before they appear in complex explanations
- [ ] **Modality:** Use visuals + text (not text + text) for complex ideas
- [ ] **Personalization:** Use conversational tone ("you" not "the learner")

### The Platform Lessons Matrix

| Platform Principle | Current Support | Gap |
|---|---|---|
| Duolingo: Session brevity | Good (15-25 min) | Could add 5-min review sessions |
| Duolingo: Spaced repetition | Weak | Need automatic review scheduling |
| Duolingo: Data-driven iteration | Weak | Need per-concept analytics |
| Khan: Mastery gating | Partial (pacing rules) | Need score thresholds for progression |
| Khan: Socratic presence | Good (agent as tutor) | Could add more "why do you think?" prompts |
| Brilliant: Interactive exploration | Good (simulator, custom) | Could expand interactive component types |
| Brilliant: Massive problem banks | Weak | Limited by per-session generation |
| Brilliant: Challenge-first design | Available (Pattern B) | Should be default, not alternative |
| Coursera: Goal alignment | Weak | Could add "by end of course you'll be able to..." framing |

---

## Sources

- Dunlosky et al. (2013). "Improving Students' Learning with Effective Learning Techniques." *Psychological Science in the Public Interest*
- Karpicke & O'Day (2024). Oxford Handbook chapter on retrieval practice principles
- Nature Reviews Psychology (2022). "The science of effective learning with spacing and retrieval practice"
- Weinstein et al. (2018). "Teaching the science of learning." *Cognitive Research: Principles and Implications*
- Frontiers in Psychology (2025). "What are the influencing factors of online learning engagement?"
- Journal of Technology and Education Meta-Review (2024). "What Factors Contribute to Effective Online Higher Education?"
- Frontiers in Education (2025). "Online vs. traditional education: scoping review"
- Online Learning Consortium (2025). "Student Perceptions of Online Course Quality"
- Columbia CCRC (2025). "Beyond Engagement: Promoting Motivation and Learning in Online Courses"
- Heliyon (2024). "Microlearning beyond boundaries: systematic review and novel framework"
- IEEE (2024). "Micro-Learning: A Comprehensive Survey"
- MIT Digital Learning Toolkit (2025). "Designing Assessments"
- SFU (2025). "Designing Online Assessments"
- Springer/Discover AI (2025). "AI in adaptive education: systematic review"
- Heliyon (2024). "Personalized adaptive learning in higher education: scoping review"
- MDPI (2025). "AI in Curriculum Design: A Data-Driven Approach"
- Quality Matters (2025). "Research-Supported Recommendations for Strategic AI Integration"
- Mayer (2024). "Past, Present, and Future of the Cognitive Theory of Multimedia Learning." *Educational Psychology Review*
- Bjork & Bjork (2011). "Making things hard on yourself, but in a good way: Creating desirable difficulties"
- Brilliant.org Engineering Blog (2025). "Hand-crafted, machine-made" and "When almost right is catastrophically wrong"
- Duolingo Blog (2025). "The Duolingo Method: 5 key principles"
- Khan Academy Blog (2026). "Motivation Meets Mastery: Khan Academy Reimagined"
- Coursera (2025). "Learner Outcomes Report"
