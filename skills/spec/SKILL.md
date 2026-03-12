---
name: spec
description: "Interviews the user about a product idea or feature using structured questions, then generates a detailed spec document (SPEC.md). Use when the user wants to flesh out an idea, plan a feature, or create a buildable specification."
metadata:
  version: 0.1.0
---

# Spec

Turn a vague idea into a buildable specification through a short, structured interview.

**Announce at start:** "I'm using the spec skill to help you define this."

## Workflow

```
Interview → Synthesize → Draft → Review → Save
```

1. **Interview** — ask structured questions to understand the idea
2. **Synthesize** — identify scope, constraints, and open questions
3. **Draft** — write a SPEC.md covering all dimensions
4. **Review** — walk through the spec with the user, revise until approved
5. **Save** — write the final spec to disk

<HARD-GATE>
Do NOT generate the spec document until you have completed the interview and the user has confirmed you understand their idea correctly. Do NOT skip to implementation. The output of this skill is a spec document, not code.
</HARD-GATE>

## Interview

Ask questions **one at a time**. Prefer multiple-choice when possible. Keep it to 5-8 questions total — infer the rest from context.

**Question sequence (adapt to context):**

1. **What is this?** — one-sentence description in the user's words
2. **Who is it for?** — target user or audience (multiple-choice if obvious candidates exist)
3. **What's the trigger?** — when/why does someone reach for this?
4. **What does success look like?** — concrete outcome, not metrics
5. **What's the scope?** — MVP vs full vision (multiple-choice: minimal / moderate / ambitious)
6. **What exists already?** — prior art, constraints, systems it must integrate with
7. **What's explicitly out of scope?** — things that might seem related but aren't part of this
8. **Any hard constraints?** — tech stack, timeline, platform, compliance, etc.

**Rules:**
- One question per message. Never batch questions.
- If the user's answer implies the next question's answer, skip it.
- If something is ambiguous, ask a follow-up before moving on.
- Mirror the user's language — don't introduce jargon they didn't use.

## Synthesis checkpoint

Before drafting, summarize what you've learned in 3-5 bullets and ask: **"Does this capture it? Anything I'm missing or got wrong?"**

Only proceed to drafting after the user confirms.

## Spec Document Format

Write the spec as a markdown document with these sections. Scale each section to the complexity of the idea — a simple feature gets a few sentences per section, not paragraphs.

```markdown
# [Feature/Product Name]

## Problem
What problem does this solve? Why does it matter?

## Solution
What are we building? One-paragraph description.

## Users
Who uses this and what's their context?

## Requirements
### Must have
- [ ] ...

### Should have
- [ ] ...

### Won't have (this version)
- [ ] ...

## Design
How it works at a high level. Architecture, key flows, data model —
whatever is relevant. Use diagrams if they clarify.

## Open questions
Unresolved decisions that need input before or during implementation.

## Out of scope
Explicitly excluded to prevent scope creep.
```

**Principles:**
- Requirements are concrete and testable, not vague ("fast" → "responds in <200ms")
- "Won't have" is just as important as "Must have"
- Open questions are honest — don't paper over unknowns
- Keep it short enough that someone will actually read it

## Saving the spec

Save to: `SPEC.md` in the project root, unless the user specifies a different location.

If a `SPEC.md` already exists, ask whether to replace or save alongside it (e.g., `SPEC-<feature-name>.md`).

## After the spec

Present the saved file path and ask what the user wants to do next. Do NOT automatically invoke implementation skills — the user decides the next step.
