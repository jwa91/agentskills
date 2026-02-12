from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture()
def tmp_skill(tmp_path: Path) -> Path:
    """Create a minimal skill directory with a valid SKILL.md."""
    skill_dir = tmp_path / "skills" / "test-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: test-skill\nmetadata:\n  version: 1.0.0\n---\n# Test Skill\nA test skill.\n"
    )
    return tmp_path
