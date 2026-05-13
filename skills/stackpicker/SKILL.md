---
name: stackpicker
description: "Advise on the stack for a new project. Given what the user wants to build, plus the user's principles and preferences, propose a language + tools as a short written proposal. Use when starting a new project or deciding what to build something in."
metadata:
  version: 0.1.0
---

# Stack Picker

**Assignment:** given the user wants to create _X_, and given these principles and preferences, what stack would you advise for this new project? Present your advice as a short proposal back to the user.

Read both references before starting:

- [references/principles.md](references/principles.md) — the user's tool-selection criteria and language-by-entrypoint defaults.
- [references/decision-tree.md](references/decision-tree.md) — the deterministic mapping from project shape to tools.

Always use the latest stable release of every tool. Do not pin or recommend version numbers. Always do some web research for the latest versions of important packages.

## Steps

1. **Decide what sort of project it is — language and surfaces.**
   - Match it against Phase 1 (language) and Phase 3 (surfaces) of the decision tree.
   - New surfaces or hybrid project types are allowed. Fit them to the closest row in the tree and call that out in the proposal.
   - This step also collapses the Phase 2 baseline (automatic, no question).

2. **Decide which additional questions are relevant.**
   - Walk Phase 4, ask only the ones gated to this language / project. Skip any whose answer is implied by the description.
   - Pick up ambient signals (secrets, dotfiles, App Store distribution, local LLM, n8n) from the description without asking.

3. **Present a short proposal.**

   Free-form Markdown. Aim for a page or less. Cover, in this order:
   - **What we're building.** One sentence echoing the user's intent.
   - **Stack at a glance.** Language(s) + the surfaces being filled.
   - **Tools.** One compact table grouping tools by what they do. Each row: tool, role, one short reason — citing a criterion from `principles.md` (modern + fast, configurable, open standards, good DX, low memory, no vendor lock-in, agent-interactable) or a project-specific signal.
   - **Anything new or off-list.** If the tree had a gap (e.g. TUI for Go, TS API framework) or the project forced a deviation from the deliberately-not-on-the-table list, name it and the reason.
   - **Open questions.** Honest unknowns the user should resolve before scaffolding.

   No version numbers. No yes/no decision Docker rows; if Docker is in scope it's because "Add to VPS" was yes. No personal-environment tools (terminal, prompt, etc.).

## Anti-patterns

- Asking about the language directly before trying to derive it from the description.
- Asking every Phase 4 question regardless of relevance.
- Producing a long structured report. The deliverable is a short proposal.
- Scaffolding code or running `init` commands. The deliverable is advice.
- Recommending anything from `decision-tree.md`'s "Deliberately not on the table" list without a named constraint.
- Pinning versions.
