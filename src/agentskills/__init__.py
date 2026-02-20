"""CLI tooling for managing agent skills."""

from __future__ import annotations

from pathlib import Path

CURATED_DIR = "curated"
REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def discover_all_skills(skills_root: Path) -> list[str]:
    """Return names of skill directories under skills/ and skills/curated/.

    Own skills (directly under skills_root) take precedence over curated
    skills with the same name.
    """
    if not skills_root.exists():
        return []

    own = [
        p.name
        for p in sorted(skills_root.iterdir())
        if p.is_dir() and p.name != CURATED_DIR and (p / "SKILL.md").exists()
    ]

    curated_root = skills_root / CURATED_DIR
    curated = []
    if curated_root.is_dir():
        curated = [
            p.name
            for p in sorted(curated_root.iterdir())
            if p.is_dir() and (p / "SKILL.md").exists() and p.name not in own
        ]

    return own + curated


def categorize_skills(skills_root: Path) -> tuple[list[str], list[str]]:
    """Return (own, curated) skill name lists.

    Own skills are directly under skills_root; curated are under
    skills_root/curated/ and not shadowed by an own skill.
    """
    if not skills_root.exists():
        return [], []

    own = [
        p.name
        for p in sorted(skills_root.iterdir())
        if p.is_dir() and p.name != CURATED_DIR and (p / "SKILL.md").exists()
    ]

    curated_root = skills_root / CURATED_DIR
    curated: list[str] = []
    if curated_root.is_dir():
        curated = [
            p.name
            for p in sorted(curated_root.iterdir())
            if p.is_dir() and (p / "SKILL.md").exists() and p.name not in own
        ]

    return own, curated


def resolve_skill_dir(skills_root: Path, skill_name: str) -> Path:
    """Resolve a skill name to its directory, checking own then curated."""
    own = skills_root / skill_name
    if own.is_dir() and (own / "SKILL.md").exists():
        return own

    curated = skills_root / CURATED_DIR / skill_name
    if curated.is_dir() and (curated / "SKILL.md").exists():
        return curated

    raise RuntimeError(
        f"Skill not found: {skill_name} "
        f"(checked {own} and {curated})"
    )
