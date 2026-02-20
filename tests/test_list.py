from __future__ import annotations

from pathlib import Path

from agentskills.list import main


class TestListCommand:
    def test_lists_own_skills(self, tmp_skill: Path, capsys, monkeypatch):
        monkeypatch.setattr(
            "sys.argv",
            ["agentskills list", "--repo-path", str(tmp_skill)],
        )
        result = main()
        assert result == 0
        out = capsys.readouterr().out
        assert "test-skill" in out
        assert "(curated)" not in out

    def test_lists_curated_skills_with_label(
        self, tmp_skill_with_curated: Path, capsys, monkeypatch
    ):
        monkeypatch.setattr(
            "sys.argv",
            ["agentskills list", "--repo-path", str(tmp_skill_with_curated)],
        )
        result = main()
        assert result == 0
        out = capsys.readouterr().out
        assert "test-skill" in out
        assert "curated-skill (curated)" in out

    def test_own_before_curated(
        self, tmp_skill_with_curated: Path, capsys, monkeypatch
    ):
        monkeypatch.setattr(
            "sys.argv",
            ["agentskills list", "--repo-path", str(tmp_skill_with_curated)],
        )
        main()
        out = capsys.readouterr().out
        lines = [line for line in out.strip().splitlines() if line.strip()]
        assert lines.index("test-skill") < lines.index("curated-skill (curated)")

    def test_no_skills_returns_error(self, tmp_path: Path, capsys, monkeypatch):
        monkeypatch.setattr(
            "sys.argv",
            ["agentskills list", "--repo-path", str(tmp_path)],
        )
        result = main()
        assert result == 1
        out = capsys.readouterr().out
        assert "No skills found" in out

    def test_defaults_to_repo_root(self, tmp_skill: Path, capsys, monkeypatch):
        monkeypatch.setattr("agentskills.list.REPO_ROOT", tmp_skill)
        monkeypatch.setattr("sys.argv", ["agentskills list"])
        result = main()
        assert result == 0
        out = capsys.readouterr().out
        assert "test-skill" in out
