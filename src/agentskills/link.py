#!/usr/bin/env python3
"""Create optional harness links to a project's .agents/skills directory."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "harness_adapters.json"


def parse_harness_list(raw_values: list[str]) -> list[str]:
    """Parse comma-separated and repeated harness names into a unique list."""
    selected: list[str] = []
    for raw in raw_values:
        for part in raw.split(","):
            harness = part.strip()
            if harness and harness not in selected:
                selected.append(harness)
    return selected


def remove_path(path: Path) -> None:
    """Remove a file, symlink, or directory tree."""
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the link command."""
    parser = argparse.ArgumentParser(
        description=("Link non-native harness skill folders to .agents/skills."),
    )
    parser.add_argument(
        "--project",
        required=True,
        help="Project directory containing .agents/skills.",
    )
    parser.add_argument(
        "--harness",
        action="append",
        default=[],
        help="Harness name(s). Repeat or comma-separate. Default: all.",
    )
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="Adapter config JSON path.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace existing non-matching link/path.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned actions without writing changes.",
    )
    return parser.parse_args()


def _link_harness(  # noqa: PLR0913
    name: str,
    link_path: Path,
    relative_target: Path,
    force: bool,
    dry_run: bool,
) -> None:
    """Create or validate a single harness symlink."""
    if link_path.is_symlink():
        existing = Path(os.readlink(link_path))
        if existing == relative_target:
            print(f"skip: {name} already linked ({link_path} -> {relative_target})")
            return
        if not force:
            raise RuntimeError(
                f"Link already exists for {name} with"
                f" different target: {link_path} ->"
                f" {existing} (use --force to replace)"
            )
        if not dry_run:
            link_path.unlink()
    elif link_path.exists():
        if not force:
            raise RuntimeError(
                f"Path already exists for {name}: {link_path} (use --force to replace)"
            )
        if not dry_run:
            remove_path(link_path)

    if dry_run:
        print(f"plan: link {name} ({link_path} -> {relative_target})")
    else:
        link_path.symlink_to(relative_target, target_is_directory=True)
        print(f"linked: {name} ({link_path} -> {relative_target})")


def main() -> int:
    """Create harness symlinks for a project."""
    try:
        args = parse_args()
        project_root = Path(args.project).expanduser().resolve()
        config_path = Path(args.config).expanduser().resolve()

        if not config_path.exists():
            raise RuntimeError(f"Config file not found: {config_path}")

        with config_path.open("r", encoding="utf-8") as handle:
            config = json.load(handle)

        canonical_rel = config.get("canonical_skills_dir")
        adapters = config.get("adapters", {})
        if not canonical_rel or not isinstance(adapters, dict):
            raise RuntimeError("Config must contain canonical_skills_dir and adapters.")

        canonical_dir = project_root / canonical_rel
        if not canonical_dir.exists():
            raise RuntimeError(
                f"Canonical skills directory is missing:"
                f" {canonical_dir}. Install skills first"
                " via `agentskills bootstrap`."
            )

        selected = parse_harness_list(args.harness)
        harness_names = selected if selected else sorted(adapters.keys())
        unknown = [name for name in harness_names if name not in adapters]
        if unknown:
            raise RuntimeError(f"Unknown harness(es): {', '.join(unknown)}")

        print(f"project: {project_root}")
        print(f"canonical: {canonical_dir}")
        print(f"dry_run: {args.dry_run}")

        for name in harness_names:
            adapter = adapters[name]
            link_rel = adapter.get("relative_link_path")
            if not link_rel:
                raise RuntimeError(f"Adapter {name} is missing relative_link_path.")

            link_path = project_root / link_rel
            link_path.parent.mkdir(parents=True, exist_ok=True)
            relative_target = Path(os.path.relpath(canonical_dir, link_path.parent))
            _link_harness(
                name,
                link_path,
                relative_target,
                args.force,
                args.dry_run,
            )

        print("done: optional harness links are configured.")
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
