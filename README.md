# Agent Skills

A personal collection of agent skills.

Agent skills are portable instruction sets that give AI coding agents (Claude Code, OpenCode, Amp, etc.) specialized capabilities. Each skill lives in its own directory under `skills/` and can be installed into any project.

## Skills

| Skill                                              | Description                                                                                                                     |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| [interactive-learner](skills/interactive-learner/) | AI tutoring skill that creates rich, interactive HTML courses with quizzes, simulators, spaced repetition, and more             |
| [mac-cleanup](skills/mac-cleanup/)                 | Interactive macOS system cleanup that discovers installed tools and frees disk space by pruning caches, dev artifacts, and more |
| [personal-commit-review](skills/personal-commit-review/) | Personal GitHub commit retrospective that collects commit activity and turns it into a prose review with stats and highlights |
| [spec](skills/spec/)                               | Interview-driven spec writing — turns a vague idea into a buildable SPEC.md through structured questions                      |

### Curated

Skills under `skills/curated/` are created by other authors. See each skill for original source and attribution.

| Skill | Description | Source |
| --- | --- | --- |
| [brainstorming](skills/curated/brainstorming/) | Explore intent, requirements and design before creative work | [obra/superpowers](https://github.com/obra/superpowers) |
| [clean-architecture](skills/curated/clean-architecture/) | Clean Architecture principles and best practices from Robert C. Martin | [pproenca/dot-skills](https://github.com/pproenca/dot-skills) |
| [session-handoff](skills/curated/session-handoff/) | Comprehensive handoff documents for seamless AI agent session transfers | [softaworks/agent-toolkit](https://github.com/softaworks/agent-toolkit) |
| [test-driven-development](skills/curated/test-driven-development/) | TDD workflow — write tests before implementation code | [obra/superpowers](https://github.com/obra/superpowers) |
| [writing-plans](skills/curated/writing-plans/) | Plan multi-step tasks from specs/requirements before touching code | [obra/superpowers](https://github.com/obra/superpowers) |

## Repository Layout

```
skills/<skill-name>/          # Own skill source directories (each contains SKILL.md)
skills/curated/<skill-name>/  # Curated skills from other authors
src/agentskills/              # CLI tooling (bootstrap, link, package, release)
tests/                        # Tests for the CLI tooling
docs/                         # Reference docs and research
```

## Getting Started

Install dev dependencies (ruff, pytest) and the `agentskills` CLI:

```bash
uv sync --extra dev
```

### Install a skill into your project

```bash
agentskills bootstrap \
  --project /path/to/your-project \
  --skill <skill-name> \
  --mode copy
```

Or from a remote clone:

```bash
agentskills bootstrap \
  --project /path/to/your-project \
  --repo-url https://github.com/jwa91/agentskills.git \
  --ref main \
  --skill <skill-name> \
  --mode copy
```

Use `--mode symlink` during development so changes in this repo are reflected immediately.

### Link for non-native harnesses

The canonical install location is `<project>/.agents/skills/`. Some agent harnesses look elsewhere — this creates symlinks for those:

```bash
agentskills link --project /path/to/your-project --force
```

Supported harnesses:

- Anthropic (`.claude/skills`)
- OpenCode (`.opencode/skills`)
- Amp (`.amp/skills`)

### Validate and package

```bash
# Validate a skill against the spec
uvx --from skills-ref agentskills validate skills/<skill-name>

# Package into a distributable .skill archive
agentskills package <skill-name> --overwrite

# Validate + package in one step
agentskills release <skill-name> --overwrite
```

Packaged artifacts are written to `dist/<skill-name>-v<version>.skill`.

## Development

```bash
# Run tests
uv run pytest

# Format / lint
uv run ruff check src tests
uv run ruff format src tests
```

## Versioning

Each skill declares its own version in `SKILL.md` under `metadata.version` (semver: `X.Y.Z`). Release tags follow the pattern `<skill-name>/v<version>`.

## External References

- [What are agent skills?](https://agentskills.io/what-are-skills.md)
- [Skills specification](https://agentskills.io/specification.md)
- [Integrating skills into your agent](https://agentskills.io/integrate-skills.md)
