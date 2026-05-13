# `agentskills` (Go)

Single-binary port of the Python CLI under `src/agentskills/`.

- **Behaviour**: see [`docs/cli-go-port-briefing.md`](../../docs/cli-go-port-briefing.md).
- **Boundary contract**: see ADR 0006 in `jwa91/homebrew-tap` (`docs/adr/0006-agentskills-boundary-contract.md`).

## Commands

| Command | Description |
|---|---|
| `bootstrap` | Copy or symlink skills into `<project>/.agents/skills/`. |
| `list` | List available skills (own + curated). |
| `link` | Symlink harness folders (`.claude/skills`, `.opencode/skills`, `.amp/skills`) into `.agents/skills`. |
| `doctor` | Verify git, cache dir, target dir, and default repo URL. |

Flags mirror the Python CLI 1:1. The harness adapter table is embedded via `//go:embed harness_adapters.json` from `internal/harness/`.

## Build

```bash
make build           # writes ./bin/agentskills
make install         # go install into $GOBIN
make test            # full suite with coverage
```

## Release

Releases are driven by `.goreleaser.yaml` at the repo root and the tag scheme `vX.Y.Z`. Per-skill tags (`<skill>/vX.Y.Z`) are ignored by goreleaser via `git.ignore_tags`.

Releases are tag-driven via GitHub Actions (`.github/workflows/release.yml`). Cut one by tagging from `main`:

```bash
git tag -a v0.1.0 -m "v0.1.0"
git push origin v0.1.0
```

The workflow runs `make check`, then `goreleaser release --clean`, then a smoke test against the published Linux amd64 archive. The cask is written directly into `jwa91/homebrew-tap/Casks/agentskills.rb` via GoReleaser `homebrew_casks`.

## Why a Go port?

- Distributes as a static binary via the user's personal Homebrew tap.
- Removes the `uv` / Python prerequisite for end users.
- Skill content stays in `skills/`; the CLI clones the repo at install time and copies files verbatim. Scripts inside `skills/<name>/scripts/` are opaque content and never executed by this CLI.
