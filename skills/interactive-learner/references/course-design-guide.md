# Course Design Guide

## The Research Phase

**Before designing a single session, research the topic thoroughly.** This is not optional — it's the foundation of every good course.

### What to research

1. **Conceptual structure** — What are the core concepts? What depends on what? What's the optimal learning order?
2. **Common misconceptions** — What do beginners consistently get wrong? What "obvious" things aren't obvious?
3. **Best existing resources** — What's the best video, article, tutorial, playground, or tool for this topic? You'll curate these, not compete with them.
4. **Real-world applications** — How is this used in practice? What are the war stories? Where does theory meet reality?
5. **The "aha moments"** — What analogies, visualizations, or exercises make this topic click? What do the best teachers do differently?

### Source priorities

1. Official documentation and specs
2. Peer-reviewed research / reputable educational content
3. Respected practitioners and educators (conference talks, well-known blogs)
4. Community-vetted resources (highly-rated tutorials, curated awesome-lists)
5. Interactive tools and sandboxes the student can actually use

### Save your research

Write research notes to a markdown file alongside the course. Include:
- Key sources with links
- Recommended deep-dives for students who want more
- Practice resources and sandboxes
- Community links (forums, Discord servers, Slack channels)

This file becomes a permanent reference for the student.

---

## Content-First Design Process

Design the *explanation* before choosing components:

1. **List what needs to be taught** — ideas, concepts, aha moments, key vocabulary
2. **Structure the narrative flow** — what order makes the lightbulbs go on?
3. **Then choose components for each piece** — which component best delivers each part of the narrative?
4. **Component variety happens naturally** when you follow content — if three story-cards in a row is the clearest way to teach something, that's fine

Don't start from "I need one of each component type." Start from "here's what I want the student to understand, and here's how I'd explain it in conversation."

---

## Topic Type → Component Selection

### Mermaid-native visual toolkit (cross-topic)

Use these when learners benefit from visual structure:

- `concept-map` — relationship structure (what connects to what)
- `mind-map` — hierarchy and prerequisite expansion (what branches from what)
- `kanban-board` — workflow/progression state (what is planned, in-progress, done)
- `radar-profile` — multi-dimensional competency snapshot (where strengths/gaps are)

Heuristic:
- If you need **structure**, use `mind-map`
- If you need **flow/progress**, use `kanban-board`
- If you need **comparison across dimensions**, use `radar-profile`
- If you need **dependency/causality links**, use `concept-map`

### Technical / Hands-On (Kubernetes, Docker, Git, AWS, Python, databases...)

- **Primary:** simulator, fill-blanks, debug-challenge, real-world-mission
- **Supporting:** quiz, vocab-cards, matching, concept-map, mind-map, kanban-board
- **Open-ended:** explain-back ("explain this error message"), roleplay ("you're the on-call engineer")
- **Real-world:** sandbox playgrounds, CLI practice, "read this real config file"
- **Video style:** Live-coding walkthroughs, architecture overviews
- **Deep-dives:** Official docs, respected books, tool-specific tutorials
- **Vocab framework:** what / why / how / watch-out

### Conceptual / Theoretical (Marketing theory, Economics, Philosophy, History...)

- **Primary:** story-card, timeline, concept-map, mind-map, sorting-game
- **Supporting:** vocab-cards, matching, quiz
- **Open-ended:** roleplay ("you're a CEO deciding..."), explain-back, open-reflection
- **Real-world:** case studies, "find a real example of X", "read this article and react"
- **Video style:** Animated explainers, documentary clips, TED talks
- **Deep-dives:** Seminal papers, books, long-form journalism
- **Vocab framework:** what / why / when-it-matters / common-misconception

### Creative (Design, Music theory, Writing, Photography...)

- **Primary:** side-by-side (before/after), sorting-game, simulator
- **Supporting:** quiz, vocab-cards
- **Open-ended:** "create something and share it", "critique this piece", roleplay ("you're the art director")
- **Real-world:** "take a photo using this principle", "sketch this concept", "visit this gallery online"
- **Video style:** Process walkthroughs, critique sessions, master classes
- **Deep-dives:** Artist portfolios, technique breakdowns, creative tools
- **Unique ideas:** "Spot the principle", "Which is better and why?", "Remix this"

### Math / Logic (Statistics, Algorithms, Proofs, Logic puzzles...)

- **Primary:** simulator (step-through), fill-blanks, debug-challenge, sorting-game
- **Supporting:** quiz, concept-map, radar-profile
- **Open-ended:** explain-back ("explain this proof in plain English"), "predict the output"
- **Real-world:** "find real data and apply this formula", visualization tools, online calculators
- **Video style:** Animated math (3Blue1Brown style), worked examples
- **Deep-dives:** Interactive visualization tools, textbook chapters, problem sets
- **Unique ideas:** "Trace the algorithm", "Find the error in this proof", "Is this optimization correct?"

### Language Learning (Spanish, Japanese, French...)

- **Primary:** matching, fill-blanks, sorting-game (sentence construction)
- **Supporting:** vocab-cards, quiz
- **Open-ended:** "write a short message using today's vocabulary", roleplay ("order food at a restaurant")
- **Real-world:** "change your phone language for 1 hour", "watch a 2-min clip without subtitles", "find a song in this language"
- **Video style:** Native speaker clips, cultural context
- **Deep-dives:** Language exchange platforms, podcast recommendations, reading material at their level
- **Unique ideas:** "Complete the conversation", "Spot the mistake", "Translate this meme"

---

## Session Structure Rules

Each session follows the **explainer → conversation → test** flow:

1. **Explainer HTML** — content-only components that teach the material
2. **Conversational checkpoint** — agent asks "Was everything clear?", discusses confusion, asks 1 teach-back question
3. **Test HTML** — scored exercises + score-summary, student gets a result code to paste back in chat

Component budget per session:
1. **Explainer:** 4-8 content components chosen to best serve learning goals (not one-of-each)
2. **Conversation:** 1 teach-back question + open discussion
3. **Test:** 3-6 scored components + score-summary
4. **0-1 real-world missions** per session (don't overwhelm with homework)
5. **1 `recommended-deep-dive`** at the end of every explainer (curated from research)

## Vocabulary Rules

- Max 6 new terms per session
- Every term needs: definition + real-world analogy bridging to what the student knows
- Prefer the "what/why/how/watch-out" framework
- Connect new terms to previously learned terms
- Tag each term with its `concept` ID for mastery tracking

## Pacing Rules

- If student scores 100% on last 2 sessions → accelerate (fewer basic exercises, more challenges, more open-ended)
- If student scores below 60% → decelerate (add review, more examples, simpler exercises)
- If concepts are fading (check `progress.py review`) → weave review into the next session
- Default: moderate pace with variety

## Session Flow Patterns (vary these!)

Each pattern now maps to the **explainer → conversation → test** structure. The explainer contains content components, the conversation includes teach-back questions, and the test contains scored exercises.

### Pattern A: Classic
**Explainer:** story-card → vocab-cards → simulator
**Conversation:** teach-back on key concept
**Test:** quiz → matching → score-summary

### Pattern B: Discovery (challenge first → explain)
**Explainer:** debug-challenge or simulator → story-card (reveal) → vocab-cards
**Conversation:** "What surprised you? Why did that happen?"
**Test:** quiz → fill-blanks → score-summary
*Productive failure improves retention. This should be the default for most topics.*

### Pattern C: Video-led
**Explainer:** video-embed → vocab-cards → story-card
**Conversation:** "What stuck out from the video?"
**Test:** quiz → matching → score-summary

### Pattern D: Comparison-driven
**Explainer:** side-by-side → story-card (why the difference?) → vocab-cards
**Conversation:** "Which approach would you pick for [scenario]?"
**Test:** matching → quiz → score-summary

### Pattern E: Deep dive
**Explainer:** concept-map → detailed story-cards → recommended-deep-dive
**Conversation:** teach-back on relationships between concepts
**Test:** fill-blanks → sorting-game → score-summary

### Pattern F: Investigation
**Explainer:** real-world-mission → story-card explaining what they'll see → vocab
**Conversation:** "What did you find? Why do you think it works that way?"
**Test:** quiz → matching → score-summary
*Start by sending them somewhere real, then explain what they experienced.*

### Pattern G: Socratic
**Explainer:** story-card (setup) → concept-map → vocab-cards
**Conversation:** prediction question → reveal → "restate in your own words"
**Test:** quiz → fill-blanks → score-summary
*Maximum cognitive engagement through hypothesize-discover-articulate.*

### Pattern H: Debug-driven (great for technical topics)
**Explainer:** debug-challenge → story-card (the concept behind the bug) → vocab
**Conversation:** "Why did that bug happen? What's the general principle?"
**Test:** fill-blanks (build it correctly) → quiz → score-summary

### Pattern I: Creative exploration (great for creative/language topics)
**Explainer:** story-card (principles) → side-by-side (good vs bad examples)
**Conversation:** roleplay scenario → discuss approach
**Test:** sorting-game → matching → score-summary

### Pattern J: Learning board
**Explainer:** kanban-board (learning workflow) → story-card explanation
**Conversation:** discuss priorities and next actions
**Test:** quiz → matching → score-summary
*Excellent for project-based learning and multi-session missions.*

### Pattern K: Profile-driven sprint
**Explainer:** radar-profile (current vs target) → story-card on weakest dimension
**Conversation:** teach-back on the targeted gap
**Test:** quiz → fill-blanks → score-summary
*Turns assessment into direction rather than judgment.*

### Pattern L: Hierarchy-first
**Explainer:** mind-map overview → story-card on one branch
**Conversation:** "How does [branch] connect to the bigger picture?"
**Test:** matching → sorting-game → score-summary
*Strong for complex domains where learners get lost in detail too early.*

## Course Length Guidelines

- **Quick intro** (3-5 sessions): Overview of a specific concept or tool
- **Standard course** (8-12 sessions): Comprehensive topic coverage
- **Deep dive** (12-20 sessions): Expert-level with projects and real-world missions

## Bridging Principle

Always connect new concepts to what the student already knows. Read their profile:

- If they know Docker → use container analogies for cloud topics
- If they know Python → use code examples in Python, not Java
- If marketing background → use business/campaign analogies
- If they cook → use kitchen/recipe analogies
- If they're a musician → use composition/harmony analogies

## Review Integration

Don't create "review sessions" that feel like review sessions. Instead:

1. **Weave weak concepts into new content** — mention a fading concept in a story-card about something new
2. **Vary the modality** — if they learned it via quiz, review it via matching or fill-blanks
3. **Increase the context** — same concept, more complex scenario
4. **Interleave** — mix concepts from different sessions in exercises
5. **Use explain-back** — having to explain a concept is the ultimate review
