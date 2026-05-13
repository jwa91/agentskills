Personal collection of agent skills. Each skill lives under `skills/<skill-name>/` and has its own `SKILL.md`, assets, scripts, and references.

Build/test

- Go CLI: `make check` from the repo root (runs `go vet`, lint, build, tests). Mirrors the local verification suite CI executes.
- Python (skill-author dev tools): `uv run pytest` runs all tests; `uv run ruff check src tests` and `uv run ruff format src tests` for linting/formatting.
- Each skill may have its own scripts for validation and building — check `skills/<skill-name>/scripts/`.

Architecture

- `skills/<skill-name>/SKILL.md` is the skill definition (metadata, instructions, references).
- `tools/agentskills/` is the **Go CLI** — the user-facing brew-installable binary (`bootstrap`, `list`, `link`, `doctor`). Distributed via `jwa91/homebrew-tap`; see `tools/agentskills/README.md` and `docs/cli-go-port-briefing.md`.
- `src/agentskills/` is the **Python package** providing skill-author dev tools:
  - `agentskills package` — build a versioned `.skill` zip archive.
  - `agentskills release` — validate then package in one step.
- `tests/` contains pytest tests for the Python skill-author tools.
- `docs/` contains reference material and research that spans multiple skills.
- `.github/workflows/` is the release pipeline. `ci.yml` runs `make check` on PRs and pushes to `main`; `release.yml` is tag-driven (`v*`) and runs goreleaser → writes `Formula/agentskills.rb` into `jwa91/homebrew-tap`.

Code style

- Go: gofmt + `go vet`. Optional `golangci-lint` if installed (config mirrors prehandover). All gated by `make check`.
- Python: formatted and linted with ruff. Config in `pyproject.toml`.
- Scripts are small utilities; keep changes minimal and prefer clear, linear logic.
- Use explicit file paths and CLI arguments; keep output paths user-configurable via flags.

Adding a new skill

- Create `skills/<new-skill>/SKILL.md` following the agent skills specification.
- Keep `description` ≤ ~280 chars and trigger-shaped (lead with "Use when…" / "Trigger when…"). See `docs/cli-go-port-briefing.md` §Context-bloat discipline — the description loads into every session in projects that install the skill, so trigger-shape it tightly.
- Add any supporting assets, scripts, or references under that skill directory.
- Update the skills table in `README.md`.

Currently included skills

- `adr-writer` — Drafts one-paragraph Architecture Decision Records for intentional design choices. See `skills/adr-writer/`.
- `env-inspector` — Safely inspects `.env` files with a keyword block, token-pattern blocklist, Shannon-entropy check, value allowlist, and `PreToolUse` path-gate hook. See `skills/env-inspector/`.
- `interactive-learner` — AI tutoring skill that creates interactive HTML courses. See `skills/interactive-learner/`.
- `mac-cleanup` — Interactive macOS system cleanup that discovers installed tools and frees disk space. See `skills/mac-cleanup/`.
- `personal-commit-review` — Personal GitHub commit retrospective; turns commit activity into prose with stats and highlights. See `skills/personal-commit-review/`.
- `spec` — Interview-driven spec writing that turns a vague idea into a buildable SPEC.md. See `skills/spec/`.
- `stackpicker` — Picks language(s), Docker yes/no, and tools for a new project. Reads per-language tool defaults from the Obsidian vault and applies the Agent-Era Codebase Principles. See `skills/stackpicker/`.
- `vps-dependency-overview` — Offline-first dependency inventory across a Docker-compose monorepo. See `skills/vps-dependency-overview/`.
- `vps-service-status` — Read-only health checks for a Dockerized VPS over SSH. See `skills/vps-service-status/`.
