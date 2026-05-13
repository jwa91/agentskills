# Tool selection criteria

Not every tool meets every criterion, but I optimize toward this set when picking what enters my stack:

- **Modern and fast.** Recent design, snappy enough to stay invisible.
- **Configurable, with the config file as the source of truth.** I want to own the config, version it in dotfiles, and grep for it. Hidden settings inside an app's binary preferences are a smell.
- **Open standards.** Markdown, AGENTS.md, JSON Schema, OCI, etc. Open standards travel between tools and outlast vendors.
- **Good DX.** Sensible defaults, clear errors, decent docs. The cost of friction is paid every day.
- **Low memory footprint.** Tools should leave room for the work, not eat the laptop.
- **No vendor lock-in.** I want exit ramps. Data should be portable, configs should be transferable.
- **Agent-interactable.** A CLI is more agent-friendly than a GUI. Plain-text config is more agent-friendly than a binary plist. Tools that expose themselves cleanly to an agent are tools I'll keep using.

When two tools tie on capability, the one that better satisfies these criteria wins. The same criteria apply one level down to coding dependencies: I prefer modern, lightweight, open-source packages whose configuration I can own in the repo. I only want to add what I actually use. All dependencies earn their place.

## Stack selection

The skill should pick a stack

Default recommendations by language:

- **Go** — preferred when shipping a single binary, building fast CLIs, lightweight APIs, Brew-distributed tools, or simple long-running services.
- **Python** — preferred for agent tooling, data work, scripting, AI workflows, FastAPI services, and projects where `import-linter` gives strong architecture enforcement.
- **TypeScript** — preferred for browser/web UI, Astro/Vite apps, frontend-heavy tools, or Node-native integrations.
- **Swift** — preferred for native macOS apps, menu bar tools, and Apple-platform UX.
- **Bash** — for glue, dotfiles, one-shot scripts. Graduate to Go (or Rust) as soon as state, parsing, or branching grow.
- **Mixed repo** — allowed when surfaces justify it, but core boundaries must stay explicit.

The report records the chosen stack and any rejected alternatives.

## Validation balance (informational — not chosen here, but downstream)

Use a ratchet profile by default:

- **Hard deterministic gates** — formatting, linting, type checking, tests, schema validation, import/package boundaries, secret scanning, build checks.
- **Soft probabilistic gates** — architecture review, naming clarity, UX judgment, plan adherence, "does this feel consistent with the repo?"
- **Flexible/advisory layer** — new conventions, unstable rules, experimental folder layouts, project-specific preferences before they have repeated failures.

Promotion rule: repeated rejection promotes from advisory text → validator warning → hard gate. A hard gate that blocks useful agent work too often gets demoted or scoped more narrowly. Every rule must have an owner, scope, rationale, and removal condition.
