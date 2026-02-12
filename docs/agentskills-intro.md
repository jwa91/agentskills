# Quick Start

Install dev dependencies and the CLI:

```bash
uv sync --extra dev
```

## Install a Skill Into a Project

```bash
agentskills bootstrap \
  --project /path/to/your-project \
  --skill <skill-name> \
  --mode copy \
  --force
```

To also create symlinks for non-native harnesses:

```bash
agentskills link --project /path/to/your-project --force
```

## Validate and Package

```bash
uvx --from skills-ref agentskills validate skills/<skill-name>
agentskills package <skill-name> --overwrite
agentskills release <skill-name> --overwrite
```

## Development

```bash
uv run pytest
uv run ruff check src tests
uv run ruff format src tests
```

## External References

- [Overview](https://agentskills.io/home.md)
- [Integrate skills into your agent](https://agentskills.io/integrate-skills.md)
- [Specification](https://agentskills.io/specification.md)
- [What are skills?](https://agentskills.io/what-are-skills.md)
