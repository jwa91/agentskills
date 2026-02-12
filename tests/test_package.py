from __future__ import annotations

from pathlib import Path

import pytest

from agentskills.package import (
    iter_skill_files,
    package_skill,
    parse_frontmatter,
)


class TestParseFrontmatter:
    def test_valid(self, tmp_path: Path):
        md = tmp_path / "SKILL.md"
        md.write_text(
            "---\nname: my-skill\nmetadata:\n  version: 2.1.0\n---\n# My Skill\n"
        )
        name, version = parse_frontmatter(md)
        assert name == "my-skill"
        assert version == "2.1.0"

    def test_top_level_version(self, tmp_path: Path):
        md = tmp_path / "SKILL.md"
        md.write_text("---\nname: x\nversion: 0.0.1\n---\nbody\n")
        name, version = parse_frontmatter(md)
        assert name == "x"
        assert version == "0.0.1"

    def test_missing_frontmatter(self, tmp_path: Path):
        md = tmp_path / "SKILL.md"
        md.write_text("# No frontmatter\n")
        with pytest.raises(RuntimeError, match="Missing YAML frontmatter"):
            parse_frontmatter(md)

    def test_missing_name(self, tmp_path: Path):
        md = tmp_path / "SKILL.md"
        md.write_text("---\nversion: 1.0.0\n---\nbody\n")
        with pytest.raises(RuntimeError, match="missing 'name'"):
            parse_frontmatter(md)

    def test_bad_semver(self, tmp_path: Path):
        md = tmp_path / "SKILL.md"
        md.write_text("---\nname: x\nversion: nope\n---\nbody\n")
        with pytest.raises(RuntimeError, match="not semver"):
            parse_frontmatter(md)


class TestIterSkillFiles:
    def test_lists_files(self, tmp_path: Path):
        (tmp_path / "SKILL.md").write_text("hi")
        (tmp_path / "sub").mkdir()
        (tmp_path / "sub" / "data.json").write_text("{}")
        files = iter_skill_files(tmp_path)
        names = [f.name for f in files]
        assert "SKILL.md" in names
        assert "data.json" in names

    def test_skips_pycache(self, tmp_path: Path):
        cache = tmp_path / "__pycache__"
        cache.mkdir()
        (cache / "mod.pyc").write_text("")
        (tmp_path / "ok.py").write_text("")
        files = iter_skill_files(tmp_path)
        assert all("__pycache__" not in f.parts for f in files)

    def test_skips_ds_store(self, tmp_path: Path):
        (tmp_path / ".DS_Store").write_text("")
        (tmp_path / "ok.py").write_text("")
        files = iter_skill_files(tmp_path)
        assert all(f.name != ".DS_Store" for f in files)


class TestPackageSkill:
    def test_creates_archive(self, tmp_skill: Path):
        archive, name, version = package_skill("test-skill", tmp_skill)
        assert archive.exists()
        assert archive.suffix == ".skill"
        assert name == "test-skill"
        assert version == "1.0.0"

    def test_overwrite_required(self, tmp_skill: Path):
        package_skill("test-skill", tmp_skill)
        with pytest.raises(RuntimeError, match="already exists"):
            package_skill("test-skill", tmp_skill, overwrite=False)

    def test_overwrite_succeeds(self, tmp_skill: Path):
        package_skill("test-skill", tmp_skill)
        archive, _, _ = package_skill("test-skill", tmp_skill, overwrite=True)
        assert archive.exists()
