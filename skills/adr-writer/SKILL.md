---
name: adr-writer
description: "Draft a one-paragraph Architecture Decision Record for an intentional design choice that future-you might want to revisit. Use when the user says ADR, architecture decision, design choice, intentional decision, document this trade-off, or wants to record why one approach won over a reasonable alternative."
metadata:
  version: 0.1.0
---

# ADR Writer

Capture intentional design choices as short, one-paragraph ADRs in the style used across jwa91 repos. The point of an ADR is the *negative space*: someone could reasonably argue the opposite, and a future reader needs to know why this side won.

## When to use

The user is about to make — or just made — a design choice that a future contributor could plausibly propose reverting. The cost of forgetting *why* the choice was made is higher than the cost of writing it down. If nobody could imagine arguing the other side in good faith, skip the ADR.

## What qualifies for an ADR

- A boundary contract between repos or modules where the violation is silent and the cost is drift.
- A "we considered X and rejected it" decision where the rejection isn't obvious from the code.
- A constraint that is *not* mechanically enforceable elsewhere (no test, no linter, no type system can catch it).
- A negative-space rule ("never do X here") whose absence in code is the whole point.
- A trade-off between two reasonable approaches where the choice depends on context outside the code.

## What does NOT qualify (the leanness rule)

- Trivial style preferences (formatting, naming) — those go in linters.
- Anything codifiable as a test or a CI check — write the test instead.
- Well-documented external standards (HTTP semantics, language idioms) — link, don't ADR.
- Implementation details that change frequently.
- Decisions obvious from reading the code.
- One-off task choices ("for this PR we did X") — those go in the PR description.
- Rules with a more-specific home (security rules → `security-ground-rules.md`, conventions → `AGENTS.md`).
- Anything that, if removed, no reviewer would later say "wait, why?".

**Rule of thumb:** if you can't imagine a future contributor proposing the opposite in good faith, it's not an ADR.

## Format

The exact one-paragraph shape used in `homebrew-tap/docs/adr/`:

```
# NNNN — <title>

**Scope.** <one sentence: what the rule covers, mechanically, in present tense>. **Why.** <one sentence: the constraint that produced it; what would be lost or duplicated if it were reverted>.
```

Single paragraph. Two bolded labels (`**Scope.**` and `**Why.**`). No headings inside the paragraph. No tables. No code blocks unless the rule's literal text *is* code (rare). The title is a complete claim — "X does Y, not Z" reads better than "X behavior".

## Numbering and naming

- Files: `NNNN-kebab-case-title.md` under `docs/adr/`.
- Numbers are sequential, 4 digits, **never renumbered**. A superseded ADR stays at its number with a one-line "Superseded by NNNN" prepended.
- The title in the filename is the rule, not the topic. `0005-no-env-files-only-op-templates.md`, not `0005-secrets-policy.md`.
- The `docs/adr/README.md` index has one line per ADR, in number order.

## Cross-references

- Within a repo: link by filename (`0006-...md`).
- Across repos: full path or URL, only when the boundary itself is the ADR's subject. Per-repo ownership rules forbid reference loops.
- The primary use of an ADR is being cited from a PR review comment when someone proposes reverting it. Write with that future comment in mind.

## Process

1. **Confirm it qualifies.** Walk the leanness rule above. If a linter, test, or existing doc is a better home, stop.
2. **Pick the next number.** Read `docs/adr/README.md` and use `NNNN+1`. Never reuse or renumber.
3. **Draft Scope + Why.** One sentence each. Present tense. Concrete. The Why should name what would be lost or duplicated if the rule were reverted.
4. **Update the index.** Add a row to `docs/adr/README.md` with the new number and a one-line title.

Sign-off check before writing: *can I imagine a future contributor proposing the opposite in good faith?* If no, don't write the ADR.
