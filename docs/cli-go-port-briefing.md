# Go port of the `agentskills` CLI — briefing

## Why

- Current CLI is Python + `uv` → installation requires `uv sync` or `uvx --from`. Not portable for users without Python tooling.
- A single static Go binary releases through the same goreleaser pipeline `prehandover` already uses → `brew install jwa91/tap/agentskills` works on a clean machine.
- Matches the `jwa-tobrew` precedent: Go CLI in `tools/<name>/`, root `.goreleaser.yaml`, formula auto-written into `jwa91/homebrew-tap`.

## Non-goals

- **Do not embed skill content in the binary.** Skills are fetched at install time (same as today's `bootstrap.py`). Skill edits never require a CLI release.
- **Do not port `package`/`release` in v1.** Those are skill-author dev tools; they stay Python under `tools/skill-author/` (or drop until a real user hits friction).
- **Do not run, validate, or shell out to Python scripts inside skills.** See the scripts section below.

## Command surface (v1)

| Command | Status | Notes |
|---|---|---|
| `bootstrap` | port | Copy/symlink skill into `<project>/.agents/skills/`. Supports `--repo-url --ref --mode {copy,symlink}`. |
| `list` | port | List skills from a local clone or remote ref. Interactive picker via `--interactive`. |
| `link` | port | Harness adapters for `.claude/skills`, `.opencode/skills`, `.amp/skills`. Adapter table embedded via `//go:embed harness_adapters.json`. |
| `doctor` | new | Same pattern as `jwa-tobrew doctor` — verify git, cache dir, harness dirs, repo reachability. |
| `package` | drop v1 | Stays Python or unimplemented. |
| `release` | drop v1 | Same. |

Skill content layout under `<project>/.agents/skills/<name>/` is unchanged — the Go CLI is a drop-in for the Python CLI.

## Skill structure conventions

The CLI treats each skill directory as opaque content. Skills follow the [agent skills specification](https://agentskills.io/specification.md):

```
skills/<name>/
  SKILL.md          # required — frontmatter + body
  scripts/          # optional — runtime tools the skill invokes (python, bash, ts, …)
  references/       # optional — docs the skill points the agent at
  assets/           # optional — templates, fixtures, sample data
```

`SKILL.md` frontmatter (lifted from the spec, plus our local conventions):

```yaml
---
name: <kebab-case-name>           # must match directory name
description: <one line, ~280 char hard cap, trigger-shaped — see below>
version: 0.1.0                     # semver, per-skill
---
```

### Scripts in `scripts/` (Python and otherwise)

Scripts in a skill are the **skill's runtime concern**, not the CLI's:

- The CLI copies them verbatim and never executes them.
- The CLI never invokes `uv`, `pip`, `npm`, `bun`, or any language-specific tooling.
- If a skill needs a runtime (python3, node, …), it declares this in `SKILL.md` under a `## Requirements` section that the agent reads when the skill activates. No separate machine-readable manifest in v1 — agents already parse SKILL.md.
- **Python scripts should be self-contained.** Two acceptable patterns:
  1. Stdlib-only (preferred for trivial helpers).
  2. PEP 723 inline metadata + `uv run --script foo.py` shebang. Carries its own deps, no `requirements.txt`, no `pyproject.toml` inside `scripts/`.
- Same rule for any language. Skill = self-contained content; CLI = transport only.
- Existing skills that ship with a `scripts/` Python folder (e.g. `interactive-learner/`) stay as-is — they already follow this contract.

## Context-bloat discipline

Every installed skill's frontmatter `description` lands in the agent's loaded skill list **for every session in that project**. The cost is real. Conventions for keeping it low:

1. **One-line, trigger-shaped descriptions.** Lead with the verbs the user types ("Use when…", "Trigger when…"), not a feature list. Hard cap ~280 chars. If you need more, the body of `SKILL.md` is the right place — that only loads on activation.
2. **Install is opt-in, per project.** No "install all" verb. `bootstrap` requires at least one `--skill <name>`. The `list --interactive` picker stays a deliberate choice, not a default.
3. **Curated skills live behind a flag.** `bootstrap --skill foo` checks own first, then curated. The interactive picker shows curated collapsed by default.
4. **No cross-skill `see also` chains.** A skill may name at most **one** related skill in its description. The current `jwa-tobrew` SKILL.md references three (`scaffold-cli`, `tap-alignment`, `tap-scaffolding`) — trim to one during migration; the rest move to body links.
5. **No skill pulls in another at install time.** The CLI has no `dependencies` field, ever. If two skills are usually used together, document it in their bodies, not in install behaviour.
6. **`SKILL.md` body should be tight too.** Body is loaded when the skill activates — it's not free either. Long primers go under `references/` and are referenced by path, not inlined.

## Distribution

Mirror `jwa-tobrew`'s layout in `homebrew-tap`:

```
agentskills/
  tools/agentskills/
    main.go
    cmd/{bootstrap,list,link,doctor}.go
    internal/harness/         # embeds harness_adapters.json
    internal/skillrepo/       # clone/cache/checkout/discover
  .goreleaser.yaml            # writes Formula/agentskills.rb into homebrew-tap
  Makefile
```

- Cache dir: `~/.cache/agentskills/repos/` (unchanged from Python).
- Default repo URL: `https://github.com/jwa91/agentskills.git`. Default ref: `main`. Override with `--repo-url --ref` or env `AGENTSKILLS_REPO` / `AGENTSKILLS_REF`.
- Release tags: `vX.Y.Z` for the binary; per-skill tags stay `<skill>/vX.Y.Z`. No collision.

## Migration order

1. Scaffold Go module under `tools/agentskills/` (mirror `tools/jwa-tobrew/`).
2. Port `bootstrap` first — it pins the internal API for skill discovery + cache.
3. Port `list` (reuses skillrepo).
4. Port `link` (embed `harness_adapters.json`).
5. Add `doctor`.
6. Goreleaser config + first `v0.1.0` tag → formula lands in the tap.
7. Migrate tap-related skills into `skills/`: `jwa-tobrew`, `scaffold-cli`, `tap-alignment`, `tap-scaffolding`.
8. Update the tap repo's bootstrap to call `agentskills bootstrap --skill jwa-tobrew --skill tap-alignment …` instead of vendoring the skills inline. Tap's `.agents/skills/` becomes generated-and-gitignored.

## Decisions

- **Tag scheme: plain `vX.Y.Z` on the repo root for the binary; per-skill tags stay `<skill>/vX.Y.Z`.** Rationale: goreleaser OSS doesn't parse prefixed tags natively; plain `vX.Y.Z` matches the prehandover pattern and avoids two-tags-per-release workarounds. Per-skill tags are filtered out of binary-release version detection via `git.ignore_tags`.

## Open questions

- Keep the Python package on PyPI for `package`/`release`, or fold those into Go later? Recommend: keep Python until a skill author hits real friction.
- `link` default: should `bootstrap` auto-link to the harness Claude detects? Recommend: **no.** Auto-linking is invisible state and violates context-bloat rule #2.
