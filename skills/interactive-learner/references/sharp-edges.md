# Sharp Edges: Anti-Patterns to Avoid

## Content Anti-Patterns

### Wall of Text
**Problem:** Dumping 5 paragraphs of explanation before any interaction.
**Fix:** Max 2 short paragraphs before the first interactive element. Use story-cards to break up text. Consider progressive reveal.

### Jargon Avalanche
**Problem:** Introducing 8+ new terms in one session.
**Fix:** Max 6 new terms per session. Each needs an analogy. Connect to what they already know.

### Assuming Knowledge
**Problem:** Using terms not yet introduced. "The kubelet on your node reports to the API server."
**Fix:** Check the student's progress. Only use vocabulary they've already learned. Introduce one thing at a time.

### Teaching to the Test
**Problem:** Quiz questions that only test recall of exact wording, not understanding.
**Fix:** Ask "what would happen if..." questions. Test application, not memorization. Use debug-challenges and explain-back exercises.

### Stale Content
**Problem:** Teaching from outdated information, old API versions, deprecated patterns.
**Fix:** Research first. Use recent sources (2024-2026). Check official docs for current best practices. Note when something is evolving rapidly.

### Skipping Research
**Problem:** Generating lesson content from general knowledge without verifying accuracy or finding the best resources.
**Fix:** Always run the research phase. Find authoritative sources. Discover what tools, sandboxes, and visualizations exist. Your lessons are only as good as your research.

## Interaction Anti-Patterns

### Open-Answer Overload
**Problem:** 5 text-area prompts in one session. Cognitive fatigue. The student starts writing one-word answers.
**Fix:** Max 1-3 open-ended components per session. Each should feel like a meaningful moment, not filler. The majority of interactions should remain click-based.

### Open Answer as Filler
**Problem:** "What do you think about pods?" — vague, unfocused, no evaluation criteria.
**Fix:** Every open-ended component needs a specific prompt, clear context, and evaluation criteria the agent can use in the debrief. Compare: "In 2-3 sentences, explain why pods are ephemeral. Hint: think about what happens during a rolling update."

### Trivial Questions
**Problem:** "True or False: Kubernetes is a container orchestrator." (too obvious)
**Fix:** Questions should require understanding, not just reading comprehension. Add plausible wrong answers. Test application.

### No Feedback
**Problem:** Just showing "Wrong" without explaining why.
**Fix:** Every wrong answer gets a brief explanation of the correct answer and WHY it's correct. Every right answer gets reinforcement and context.

### Only One Interaction Type
**Problem:** 6 multiple choice quizzes in a row.
**Fix:** Vary components: quiz → matching → simulator → fill-blanks → explain-back. No two consecutive sections should use the same component type.

### Mission Overload
**Problem:** 3 real-world missions in one session ("go here, then build this, then ask someone...")
**Fix:** Max 1 real-world mission per session. It should feel like an exciting bonus, not homework. Make it genuinely interesting.

## Pacing Anti-Patterns

### The Firehose
**Problem:** Covering too much in one session. Cognitive overload.
**Fix:** One core concept per session with 2-3 supporting ideas. 20-30 minutes max.

### The Plateau
**Problem:** Every session feels the same difficulty. No progression.
**Fix:** Gradually increase complexity. Use boss challenges at module boundaries. Introduce open-ended components as the student matures.

### No Review
**Problem:** Never referencing previous sessions. Concepts fade.
**Fix:** Check concept mastery via `progress.py review`. Weave fading concepts into new sessions. Review should feel like application, not repetition.

### Ignoring the Debrief
**Problem:** Collecting open answers and missions but never following up.
**Fix:** ALWAYS debrief after a session. Discuss explain-back responses. Ask about missions. This is where the deepest learning happens.

## Video Anti-Patterns

### Video Without Context
**Problem:** "Here's a video about Kubernetes." (no framing)
**Fix:** Always provide: intro ("Watch for how they explain X"), a skip option, and a follow-up activity.

### Video Replacing the Lesson
**Problem:** The video IS the lesson, with a quiz after.
**Fix:** Videos complement interactive content, never replace it. Use `recommended-deep-dive` for longer videos students can watch optionally.

## Structural Anti-Patterns

### Missing Motivation
**Problem:** Jumping into "how" without "why." ("Here's how to create a Pod...")
**Fix:** Always start with the problem or story that motivates the concept. Challenge-first patterns work well here.

### No Bridging
**Problem:** Teaching Kubernetes without connecting to their Docker experience.
**Fix:** Read the student profile. Always bridge from what they know. Use their world for analogies.

### Inconsistent Scoring
**Problem:** Some exercises count for score, others don't, with no clear pattern.
**Fix:** Click-based interactive exercises (quiz, matching, fill-blanks, sorting) count toward the session score. Open-ended components (explain-back, roleplay, etc.) are evaluated in the debrief, not auto-scored.

### Generic Achievements
**Problem:** "Complete 5 lessons" — meaningless, doesn't reflect what was actually learned.
**Fix:** Generate achievements specific to the course and topic. "First Deployment" for a K8s course, "Color Theory Master" for a design course. Achievements should celebrate understanding, not just completion.

### Linear-Only Progression
**Problem:** Forcing Session 1 → 2 → 3 → ... with no choice.
**Fix:** After the first few sessions, offer branching: "Do you want to go deeper on X, or move on to Y?" Learner agency improves motivation. The curriculum is a guide, not a prison.
