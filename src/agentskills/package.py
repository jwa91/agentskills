#!/usr/bin/env python3
"""Package a skill directory into a versioned .skill archive."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")


def parse_frontmatter(skill_md: Path) -> tuple[str, str]:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise RuntimeError(f"Missing YAML frontmatter in {skill_md}")

    parts = text.split("---", 2)
    if len(parts) < 3:
        raise RuntimeError(f"Invalid YAML frontmatter in {skill_md}")

    frontmatter = parts[1]
    name: str | None = None
    version: str | None = None
    in_metadata = False

    for raw_line in frontmatter.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip(" "))
        if indent == 0:
            in_metadata = stripped == "metadata:"
            if stripped.startswith("name:"):
                name = stripped.split(":", 1)[1].strip().strip('"').strip("'")
            elif stripped.startswith("version:"):
                version = stripped.split(":", 1)[1].strip().strip('"').strip("'")
            continue

        if in_metadata and stripped.startswith("version:"):
            version = stripped.split(":", 1)[1].strip().strip('"').strip("'")

    if not name:
        raise RuntimeError(f"Frontmatter is missing 'name' in {skill_md}")
    if not version:
        raise RuntimeError(f"Frontmatter is missing 'metadata.version' (or 'version') in {skill_md}")
    if not SEMVER_RE.match(version):
        raise RuntimeError(f"Version is not semver ({version}) in {skill_md}")
    return name, version


def iter_skill_files(skill_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(skill_dir.rglob("*")):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts:
            continue
        if path.name in {".DS_Store"}:
            continue
        files.append(path)
    return files


def package_skill(
    skill_name: str,
    repo_root: Path,
    output_dir: str = "dist",
    overwrite: bool = False,
) -> tuple[Path, str, str]:
    """Package a skill and return (archive_path, frontmatter_name, version)."""
    skill_dir = repo_root / "skills" / skill_name
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        raise RuntimeError(f"Skill not found: {skill_md}")

    frontmatter_name, version = parse_frontmatter(skill_md)
    package_name = f"{frontmatter_name}-v{version}.skill"
    out = (repo_root / output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    archive_path = out / package_name

    if archive_path.exists() and not overwrite:
        raise RuntimeError(f"Package already exists: {archive_path} (use --overwrite to replace)")

    files = iter_skill_files(skill_dir)
    with ZipFile(archive_path, mode="w", compression=ZIP_DEFLATED) as zf:
        for file_path in files:
            zf.write(
                file_path,
                Path(frontmatter_name) / file_path.relative_to(skill_dir),
            )

    return archive_path, frontmatter_name, version


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Package a skill into a .skill archive.")
    parser.add_argument("skill", help="Skill name under skills/<skill>.")
    parser.add_argument(
        "--repo-root",
        default=str(Path.cwd()),
        help="Repo root path (default: cwd).",
    )
    parser.add_argument(
        "--output-dir",
        default="dist",
        help="Output directory for .skill files.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing package file.",
    )
    return parser.parse_args()


def main() -> int:
    try:
        args = parse_args()
        repo_root = Path(args.repo_root).expanduser().resolve()
        archive_path, name, version = package_skill(
            skill_name=args.skill,
            repo_root=repo_root,
            output_dir=args.output_dir,
            overwrite=args.overwrite,
        )
        print(f"skill: {name}")
        print(f"version: {version}")
        print(f"archive: {archive_path}")
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
