from __future__ import annotations

from pathlib import Path

import pytest

SKILL_MD_CONTENT = (
    "---\n"
    "name: test-skill\n"
    "metadata:\n"
    "  version: 1.0.0\n"
    "---\n"
    "# Test Skill\n"
    "A test skill.\n"
)


CURATED_SKILL_MD_CONTENT = (
    "---\n"
    "name: curated-skill\n"
    "metadata:\n"
    "  version: 0.5.0\n"
    "---\n"
    "# Curated Skill\n"
    "A curated skill.\n"
)


@pytest.fixture()
def tmp_skill(tmp_path: Path) -> Path:
    """Create a minimal skill directory with a valid SKILL.md."""
    skill_dir = tmp_path / "skills" / "test-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(SKILL_MD_CONTENT)
    return tmp_path


@pytest.fixture()
def tmp_skill_with_curated(tmp_skill: Path) -> Path:
    """Extend tmp_skill with a curated skill."""
    curated_dir = tmp_skill / "skills" / "curated" / "curated-skill"
    curated_dir.mkdir(parents=True)
    (curated_dir / "SKILL.md").write_text(CURATED_SKILL_MD_CONTENT)
    return tmp_skill
