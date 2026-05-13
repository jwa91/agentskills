---
name: jwa-tobrew
description: Use the `jwa-tobrew` CLI to publish a project to the user's personal Homebrew tap. Trigger when the user says "publish to my tap", "add to brew", "make this installable via brew", or asks about the `jwa-tobrew` command surface.
---

# jwa-tobrew — publish a project to the personal Homebrew tap

`jwa-tobrew` is the CLI that publishes to the tap repo at <https://github.com/jwa91/homebrew-tap>. Its own source lives at <https://github.com/jwa91/jwa-tobrew> (extracted from the tap per ADR 0008). It publishes Go binaries via GoReleaser `homebrew_casks`, macOS apps as Casks, and exceptional single-asset Formulae when a Cask is not appropriate. It is one of the `jwa-*` family; related CLIs are integrated by process boundary, not source imports (ADR 0009).

## Command surface

```
jwa-tobrew add <github-url>     Snapshot a published GitHub release into the tap (no token)
jwa-tobrew align                Report (or --apply) drift from current tap conventions
jwa-tobrew bump <name> [ver]    Re-sync an existing tap entry to a published release
jwa-tobrew completion <shell>   Generate shell completion for bash, zsh, or fish
jwa-tobrew config               Regenerate tap.toml + tap.local.toml + README items table
jwa-tobrew deps                 Show dependency overview for every item in the tap
jwa-tobrew doctor               Check tools, tap location, SSH origin, env
jwa-tobrew init                 Scaffold release config in the current project
jwa-tobrew lint                 Run the jwa-* family policy lint rules
jwa-tobrew release              Tag, GitHub release, and update the tap (run inside a project)
jwa-tobrew upgrade              Re-install via brew
jwa-tobrew version              Print build info
```

`-h` / `--help` on any subcommand prints flags.

## Security model

`jwa-tobrew` **never touches secret storage directly**. It reads `$GITHUB_TOKEN` from its environment for any command that hits the GitHub API (`release`, `bump`); commands that don't (`add`, `align`, `doctor`, etc.) need no token. Pushes to the tap go over SSH, never HTTPS-with-token (per ADR 0002).

The canonical wrapper is `jwa-harden run -- jwa-tobrew <cmd>` ([`jwa-harden`](https://github.com/jwa91/jwa-harden) walks up from `$PWD` to find the nearest `.env.template` and execs `op run --env-file=<found> -- <cmd>`). `op run --env-file=.env.template -- jwa-tobrew <cmd>` works the same way but requires you to be at the repo root and to know the path; prefer the wrapper. The `.env.template` itself holds `op://` references that are resolved into the child process for the duration of the command; never check in a real `.env`.

The full security model lives at `~/dotfiles/docs/security-ground-rules.md` and the ADRs at `docs/adr/`. Read those before suggesting any token-handling change.

## Two release patterns the tap accepts

1. **`jwa-tobrew`-managed** — single-asset items (casks, simple formulas). The CLI tags, releases, hashes, writes the `.rb`, commits to the tap. `bump`/`release` own these.
2. **Source-repo-managed** — Go CLIs and other projects whose own `.goreleaser.yaml` writes `Casks/<name>.rb` directly to the tap via `homebrew_casks`. `bump`/`release` *refuse* multi-asset entries (they have multiple `url` lines per platform; `jwa-tobrew` would corrupt them). Updates happen via `goreleaser release` in the source repo.

Detection: `AssetCount(.rb body) > 1` ⇒ source-repo-managed.

## Scaffolding (per-kind)

`jwa-tobrew init` auto-detects:

- **Go** (`go.mod`) → writes `.goreleaser.yaml` only. Releases via `goreleaser release --clean` (local or CI tag-driven).
- **Swift/macOS app** (`*.xcodeproj`, `*.xcworkspace`, `Package.swift`) → `--kind=swift-cask`, writes `scripts/release.sh` for cask publishing.
- **Other binary** → pass `--kind formula` or `--kind cask` and provide the artifact path at release time.
- **VPS/service repo** (`docker-compose.yml`, `compose.yml`) → `--kind=vps`, scaffolds the agent/security contract only until a deploy backend exists.

All kinds also get `.env.template`, `.gitignore` `.env` block, the generic `release` and `jwa-harden` skills installed by `agentskills`, harness symlinks, and a minimal `AGENTS.md` / Cursor rule contract.

For deeper walk-through of starting a new CLI from scratch, use the `scaffold-cli` skill.

## After every item-touching commit

`add`, `bump`, and `release` all regenerate `tap.toml` and the README items table (between `<!-- BEGIN ITEMS -->` markers) and commit them alongside the `.rb`. There is no separate "refresh README" step.

## Conventions enforced by the repo

- Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`, `perf:`, `build:`, `ci:`, `style:`, `revert:`) — required by the `prek` commit-msg hook
- Semver tags with `v` prefix (`v0.1.0`)
- Filename = item name (`Casks/foo.rb` ↔ name `foo`)
- For Go: `--version` flag must work (GoReleaser ldflags wire `main.version`)
- ADRs document the *why* for non-obvious choices; `CHANGELOG.md` records every meaningful change

If a change touches the tap or any project that publishes to it, run `jwa-tobrew align` (or commit through `prek`, which runs it automatically) before considering the change done. See the `tap-alignment` skill.

## Common errors

- **`$GITHUB_TOKEN not set`** — wrap with `jwa-harden run --` (or fall back to `op run --env-file=.env.template --` directly).
- **`tap origin is HTTPS but jwa-tobrew pushes over SSH only`** — `git -C ~/developer/homebrew-tap remote set-url origin git@github.com:OWNER/REPO.git`.
- **`X.rb has N url lines (multi-platform); jwa-tobrew can't safely bump it`** — this is a source-repo-managed item; release it from its own repo via `goreleaser release`, not from the tap.
- **`could not locate homebrew-tap clone`** — `export BREWTAP_DIR=/path/to/homebrew-tap`.
- **Sha256 mismatch on a fresh install** — `jwa-tobrew bump <name>`; the asset was likely re-uploaded.
