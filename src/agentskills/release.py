#!/usr/bin/env python3
"""Validate and package a skill in one command."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from agentskills.package import package_skill


def run_command(cmd: list[str], cwd: Path) -> None:
    """Run a shell command, raising on non-zero exit."""
    result = subprocess.run(cmd, cwd=str(cwd), check=False)
    if result.returncode != 0:
        joined = " ".join(cmd)
        raise RuntimeError(f"Command failed: {joined}")


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the release command."""
    parser = argparse.ArgumentParser(
        description="Validate and package a skill.",
    )
    parser.add_argument("skill", help="Skill name under skills/<skill>.")
    parser.add_argument(
        "--repo-root",
        default=str(Path.cwd()),
        help="Repo root path (default: cwd).",
    )
    parser.add_argument(
        "--output-dir",
        default="dist",
        help="Output directory for packaged .skill files.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing package file.",
    )
    parser.add_argument(
        "--skip-validate",
        action="store_true",
        help="Skip skills-ref validation.",
    )
    return parser.parse_args()


def main() -> int:
    """Validate a skill and package it."""
    try:
        args = parse_args()
        repo_root = Path(args.repo_root).expanduser().resolve()
        skill_dir = repo_root / "skills" / args.skill
        if not skill_dir.exists():
            raise RuntimeError(f"Skill path not found: {skill_dir}")

        if not args.skip_validate:
            print(f"validate: {skill_dir}")
            run_command(
                [
                    "uvx",
                    "--from",
                    "skills-ref",
                    "agentskills",
                    "validate",
                    str(skill_dir),
                ],
                cwd=repo_root,
            )
        else:
            print("validate: skipped")

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
