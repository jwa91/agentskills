from __future__ import annotations

from pathlib import Path

import pytest

from agentskills.bootstrap import (
    discover_available_skills,
    install_skill,
    main,
    parse_skill_list,
    repo_cache_name,
)

URL = "https://github.com/jwa91/agentskills"


class TestParseSkillList:
    def test_empty(self):
        assert parse_skill_list([]) == []

    def test_single(self):
        assert parse_skill_list(["foo"]) == ["foo"]

    def test_comma_separated(self):
        assert parse_skill_list(["foo,bar,baz"]) == [
            "foo",
            "bar",
            "baz",
        ]

    def test_mixed(self):
        assert parse_skill_list(["foo,bar", "baz"]) == [
            "foo",
            "bar",
            "baz",
        ]

    def test_deduplicates(self):
        assert parse_skill_list(["foo,foo", "foo"]) == ["foo"]

    def test_strips_whitespace(self):
        assert parse_skill_list([" foo , bar "]) == ["foo", "bar"]


class TestRepoCacheName:
    def test_simple_url(self):
        assert repo_cache_name(f"{URL}.git") == "agentskills"

    def test_no_git_suffix(self):
        assert repo_cache_name(URL) == "agentskills"

    def test_trailing_slash(self):
        assert repo_cache_name(f"{URL}/") == "agentskills"

    def test_special_chars(self):
        result = repo_cache_name("https://example.com/my repo!.git")
        assert all(ch.isalnum() or ch in ("-", "_", ".") for ch in result)


class TestDiscoverAvailableSkills:
    def test_finds_skills(self, tmp_skill: Path):
        skills = discover_available_skills(tmp_skill / "skills")
        assert skills == ["test-skill"]

    def test_ignores_dirs_without_skill_md(self, tmp_path: Path):
        skills_dir = tmp_path / "skills"
        (skills_dir / "not-a-skill").mkdir(parents=True)
        assert discover_available_skills(skills_dir) == []

    def test_missing_dir(self, tmp_path: Path):
        assert discover_available_skills(tmp_path / "nonexistent") == []


class TestInstallSkill:
    def test_copy_mode(self, tmp_skill: Path, tmp_path: Path):
        dest = tmp_path / "dest"
        dest.mkdir()
        result = install_skill(
            "test-skill",
            tmp_skill / "skills",
            dest,
            "copy",
            force=False,
        )
        assert result.exists()
        assert (result / "SKILL.md").exists()

    def test_symlink_mode(self, tmp_skill: Path, tmp_path: Path):
        dest = tmp_path / "dest"
        dest.mkdir()
        result = install_skill(
            "test-skill",
            tmp_skill / "skills",
            dest,
            "symlink",
            force=False,
        )
        assert result.is_symlink()

    def test_force_replaces(self, tmp_skill: Path, tmp_path: Path):
        dest = tmp_path / "dest"
        dest.mkdir()
        install_skill(
            "test-skill",
            tmp_skill / "skills",
            dest,
            "copy",
            force=False,
        )
        result = install_skill(
            "test-skill",
            tmp_skill / "skills",
            dest,
            "copy",
            force=True,
        )
        assert result.exists()

    def test_no_force_raises(self, tmp_skill: Path, tmp_path: Path):
        dest = tmp_path / "dest"
        dest.mkdir()
        install_skill(
            "test-skill",
            tmp_skill / "skills",
            dest,
            "copy",
            force=False,
        )
        with pytest.raises(RuntimeError, match="already exists"):
            install_skill(
                "test-skill",
                tmp_skill / "skills",
                dest,
                "copy",
                force=False,
            )


class TestSymlinkWarning:
    def test_symlink_mode_prints_warning(self, tmp_skill: Path, tmp_path: Path, capsys, monkeypatch):
        dest = tmp_path / "project"
        dest.mkdir()
        monkeypatch.setattr(
            "sys.argv",
            [
                "agentskills",
                "--project",
                str(dest),
                "--skill",
                "test-skill",
                "--mode",
                "symlink",
                "--repo-path",
                str(tmp_skill),
            ],
        )
        result = main()
        assert result == 0
        captured = capsys.readouterr()
        assert "symlink mode creates links that resolve outside" in captured.err

    def test_copy_mode_no_warning(self, tmp_skill: Path, tmp_path: Path, capsys, monkeypatch):
        dest = tmp_path / "project"
        dest.mkdir()
        monkeypatch.setattr(
            "sys.argv",
            [
                "agentskills",
                "--project",
                str(dest),
                "--skill",
                "test-skill",
                "--mode",
                "copy",
                "--repo-path",
                str(tmp_skill),
            ],
        )
        result = main()
        assert result == 0
        captured = capsys.readouterr()
        assert "symlink" not in captured.err
