This is a monorepo for agent skills built by jwa91. Each skill lives under `skills/<skill-name>/` and has its own `SKILL.md`, assets, scripts, and references.

Build/test

- `uv run pytest` runs all tests.
- `uv run ruff check src tests` and `uv run ruff format src tests` for linting/formatting.
- Each skill may have its own scripts for validation and building — check `skills/<skill-name>/scripts/`.

Architecture

- `skills/<skill-name>/SKILL.md` is the skill definition (metadata, instructions, references).
- `src/agentskills/` is the Python package providing the `agentskills` CLI with subcommands:
  - `agentskills bootstrap` — install a skill into a target project (copy or symlink).
  - `agentskills link` — create symlinks for agent harnesses that don't read `.agents/skills/` natively.
  - `agentskills package` — build a versioned `.skill` zip archive.
  - `agentskills release` — validate then package in one step.
- `tests/` contains pytest tests for the CLI tooling.
- `docs/` contains reference material and research that spans multiple skills.

Code style

- Python: formatted and linted with ruff. Config in `pyproject.toml`.
- Scripts are small utilities; keep changes minimal and prefer clear, linear logic.
- Use explicit file paths and CLI arguments; keep output paths user-configurable via flags.

Adding a new skill

- Create `skills/<new-skill>/SKILL.md` following the agent skills specification.
- Add any supporting assets, scripts, or references under that skill directory.
- Update the skills table in `README.md`.

Currently included skills

- `interactive-learner` — AI tutoring skill that creates interactive HTML courses. See `skills/interactive-learner/` for skill-specific architecture, scripts, and references.
