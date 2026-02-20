#!/usr/bin/env python3
"""List available skills."""

from __future__ import annotations

import argparse
from pathlib import Path

from agentskills import REPO_ROOT, categorize_skills


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the list command."""
    parser = argparse.ArgumentParser(
        description="List available agent skills.",
    )
    parser.add_argument(
        "--repo-path",
        help="Use a local repo path instead of the current directory.",
    )
    return parser.parse_args()


def main() -> int:
    """Print available skills grouped by own/curated."""
    args = parse_args()

    if args.repo_path:
        skills_root = Path(args.repo_path).expanduser().resolve() / "skills"
    else:
        skills_root = REPO_ROOT / "skills"

    own, curated = categorize_skills(skills_root)

    if not own and not curated:
        print(f"No skills found under: {skills_root}")
        return 1

    for name in own:
        print(name)
    for name in curated:
        print(f"{name} (curated)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
