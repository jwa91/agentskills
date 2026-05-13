# Decision tree

Deterministic mapping from project shape to tools. New project types or surfaces are allowed — fit them to the closest branch and call that out in the proposal.

## Phase 1 — Language

Derive from the description when possible (see `principles.md` → Stack selection). Ask only if ambiguous.

```
Go · Python · TypeScript · Swift · Bash · Multiple
```

Native Apple anywhere → Swift. No further Swift-specific picks needed.

## Phase 2 — Baseline (automatic, no question)

Every project gets these. Strict typing + lint + format + test + runtime validation + pre-commit enforcement.

| Language | Baseline |
| --- | --- |
| **Go** | `go` · `golangci-lint` (with `gofumpt`) · `gotestsum` · `govulncheck` · `prek` + `gitleaks` |
| **Python** | `uv` · `ruff` · `pyright` *or* `ty` · `pytest` · `pydantic` · `prek` + `gitleaks` |
| **TypeScript** | `pnpm` *or* `bun` · `tsc` strict · `biome` · `vitest` · `zod` · `prek` + `gitleaks` |
| **Swift** | `swiftpm` · `swift-format` · `swift-testing` · `xcbeautify` · `prek` + `gitleaks` |
| **Bash** | `shellcheck` · `set -euo pipefail` prelude · `prek` + `gitleaks` |

Tie-breaks (no question, decide from project signal):

- **Python type checker:** new project or speed-sensitive → `ty`; large codebase or needs a plugin pyright supports → `pyright`.
- **TS package manager:** monorepo / React / general Node → `pnpm`; CLI or server fully on Bun runtime → `bun`.
- **TS validation:** general → `zod`; browser bundle size matters → `valibot`.

## Phase 3 — Surfaces (multi-select; one question)

```
What does this expose? (pick all that apply)

[ ] CLI
[ ] TUI
[ ] Web UI — content-heavy (blog, docs, marketing)
[ ] Web UI — app-heavy (SPA, dashboard)
[ ] HTTP API
[ ] Background service / daemon
[ ] Library
[ ] (something else — describe; fit to the closest row)
```

| Surface | Go | Python | TypeScript |
| --- | --- | --- | --- |
| CLI | `cobra` | `typer` | (bin via `package.json`) |
| TUI | *(no curated default — recommend `bubbletea` if asked, flag as new pick)* | *(no curated default — recommend `textual` if asked, flag as new pick)* | — |
| Web UI — content | — | — | `astro` |
| Web UI — app | — | — | `vite` + React (+ `zustand` for non-trivial state) |
| HTTP API | `chi` | `fastapi` + `uvicorn` + `httpx` | *(no curated default — recommend `hono` or stdlib, flag as new pick)* |
| Background / daemon | `slog` (stdlib) + `air` for dev | `structlog` | `pino` |
| Library | — | `hatchling` *or* `uv-build` build backend | (`tsc --build` only — no bundler default yet) |

Swift is omitted on purpose: native Apple runs the Swift baseline.

## Phase 4 — Relevant follow-up questions

Ask only the ones that fit the picked language and surfaces. Skip questions whose answer is obvious from earlier replies.

| # | Question | Asked when | If YES, add |
| --- | --- | --- | --- |
| 1 | **Database persistence?** | always | `postgresql`; Go adds `sqlc` |
| 2 | **Add to VPS?** | always | `caddy` (TLS / reverse proxy), `prometheus` + `cadvisor`, `grafana` if observability is in scope; expect Docker as the deploy path (`hadolint-py` for Dockerfile lint) |
| 3 | **Add to brew?** | Go only | `goreleaser` (cross-compile + Homebrew tap formula) |
| 4 | **Architecture rules to enforce?** | Python only | `import-linter` (+ `grimp` for inspection) |
| 5 | **Task runner needed?** (>2 repeat commands) | always | `just` by default; `make` only if the project must integrate with a Makefile ecosystem |

## Ambient signals (no question, detect from description)

If the user volunteers any of these in the project description, fold the tools in without asking:

- **Secrets at runtime** → `1password-cli` + `1password-environments`
- **Lives in / installed by dotfiles** → bias toward Bash; install via `dotbot`
- **macOS app outside the App Store** → `sparkle` (auto-update via appcast)
- **Local LLM in scope** → `ollama`; `exo` if RAM-pooling across devices
- **Workflow glue across services** → `n8n`

## Deliberately not on the table

- ESLint + Prettier (use `biome`), Black/isort/flake8 (use `ruff`), pip/poetry/pyenv/pipx/virtualenv (use `uv`), mypy (use `pyright` or `ty`), Jest (use `vitest`), npm/yarn (use `pnpm` or `bun`), Make as default (use `just`), SwiftLint and SwiftFormat (use `swift-format`), XCTest (use `swift-testing`), `xcpretty` (use `xcbeautify`), `pre-commit` Python tool (use `prek`).
- **`blacksmith`** — not used. Default GitHub Actions runners are enough until proven otherwise.
- **Personal env tools** (terminal, prompt, fuzzy finder, browsers, launcher) — never project deps.

If the user pushes outside this list, treat it as a deviation: name the constraint forcing it, and confirm it still satisfies the criteria in `principles.md`.
