#!/usr/bin/env python3
"""Install one or more skills into a project's .agents/skills directory."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_CACHE_DIR = Path.home() / ".cache" / "agentskills" / "repos"
PROJECT_SKILLS_DIR = Path(".agents") / "skills"


def run_command(
    cmd: list[str],
    cwd: Path | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Run a shell command, raising on failure when check is True."""
    result = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        check=False,
        text=True,
        capture_output=True,
    )
    if check and result.returncode != 0:
        joined = " ".join(cmd)
        raise RuntimeError(f"Command failed ({joined}): {result.stderr.strip()}")
    return result


def parse_skill_list(raw_values: list[str]) -> list[str]:
    """Parse comma-separated and repeated skill names into a unique list."""
    parsed: list[str] = []
    for raw in raw_values:
        for part in raw.split(","):
            skill = part.strip()
            if skill and skill not in parsed:
                parsed.append(skill)
    return parsed


def repo_cache_name(repo_url: str) -> str:
    """Derive a filesystem-safe cache directory name from a repo URL."""
    trimmed = repo_url.rstrip("/")
    name = trimmed.rsplit("/", 1)[-1]
    if name.endswith(".git"):
        name = name[:-4]
    safe = "".join(
        ch if (ch.isalnum() or ch in ("-", "_", ".")) else "-" for ch in name
    )
    return safe or "skills-repo"


def clone_or_update_repo(repo_url: str, ref: str, cache_dir: Path) -> Path:
    """Clone or fetch+checkout a repo into the local cache."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    repo_path = cache_dir / repo_cache_name(repo_url)

    if not repo_path.exists():
        run_command(["git", "clone", repo_url, str(repo_path)])
    else:
        run_command(
            ["git", "fetch", "--all", "--tags", "--prune"],
            cwd=repo_path,
        )

    run_command(["git", "checkout", ref], cwd=repo_path)
    pull_result = run_command(["git", "pull", "--ff-only"], cwd=repo_path, check=False)
    not_on_branch = "not currently on a branch" not in pull_result.stderr.lower()
    if pull_result.returncode != 0 and not_on_branch:
        print(
            f"warning: pull skipped: {pull_result.stderr.strip()}",
            file=sys.stderr,
        )
    return repo_path


def discover_available_skills(skills_root: Path) -> list[str]:
    """Return names of subdirectories containing a SKILL.md."""
    if not skills_root.exists():
        return []
    return [
        path.name
        for path in sorted(skills_root.iterdir())
        if path.is_dir() and (path / "SKILL.md").exists()
    ]


def remove_path(path: Path) -> None:
    """Remove a file, symlink, or directory tree."""
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)


def install_skill(
    skill_name: str,
    source_root: Path,
    destination_root: Path,
    mode: str,
    force: bool,
) -> Path:
    """Copy or symlink a single skill into the destination."""
    source_skill = source_root / skill_name
    if not source_skill.exists():
        raise RuntimeError(f"Skill not found in source repo: {source_skill}")

    destination_skill = destination_root / skill_name
    if destination_skill.exists() or destination_skill.is_symlink():
        if not force:
            raise RuntimeError(
                f"Destination already exists: {destination_skill}"
                " (use --force to replace)"
            )
        remove_path(destination_skill)

    if mode == "copy":
        shutil.copytree(source_skill, destination_skill)
    else:
        destination_skill.symlink_to(source_skill.resolve(), target_is_directory=True)
    return destination_skill


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the bootstrap command."""
    parser = argparse.ArgumentParser(
        description="Bootstrap agent skills into a project.",
    )
    parser.add_argument("--project", required=True, help="Target project path.")
    parser.add_argument(
        "--skill",
        action="append",
        default=[],
        help="Skill name(s). Repeat or comma-separate. Default: all.",
    )
    parser.add_argument(
        "--mode",
        choices=["copy", "symlink"],
        default="copy",
        help="Install mode.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace destination skill if it already exists.",
    )
    parser.add_argument("--repo-url", help="Git URL to clone/pull from.")
    parser.add_argument(
        "--repo-path",
        help="Use a local repo path instead of cloning.",
    )
    parser.add_argument(
        "--ref",
        default="main",
        help="Git branch or tag when --repo-url is used.",
    )
    parser.add_argument(
        "--cache-dir",
        default=str(DEFAULT_CACHE_DIR),
        help="Clone cache directory.",
    )
    return parser.parse_args()


def resolve_repo_root(args: argparse.Namespace) -> Path:
    """Determine the repo root from CLI arguments."""
    if args.repo_path and args.repo_url:
        raise RuntimeError("Use either --repo-path or --repo-url, not both.")

    if args.repo_path:
        repo_root = Path(args.repo_path).expanduser().resolve()
        if not repo_root.exists():
            raise RuntimeError(f"Repo path does not exist: {repo_root}")
        return repo_root

    if args.repo_url:
        return clone_or_update_repo(
            repo_url=args.repo_url,
            ref=args.ref,
            cache_dir=Path(args.cache_dir).expanduser().resolve(),
        )

    return Path.cwd().resolve()


def main() -> int:
    """Bootstrap skills into a target project."""
    try:
        args = parse_args()
        repo_root = resolve_repo_root(args)

        skills_root = repo_root / "skills"
        available = discover_available_skills(skills_root)
        if not available:
            raise RuntimeError(f"No skills found under: {skills_root}")

        requested = parse_skill_list(args.skill)
        selected = requested if requested else available
        unknown = [name for name in selected if name not in available]
        if unknown:
            raise RuntimeError(
                f"Unknown skill(s): {', '.join(unknown)}. "
                f"Available: {', '.join(available)}"
            )

        project_root = Path(args.project).expanduser().resolve()
        project_root.mkdir(parents=True, exist_ok=True)
        destination_root = project_root / PROJECT_SKILLS_DIR
        destination_root.mkdir(parents=True, exist_ok=True)

        installed: list[Path] = []
        for skill_name in selected:
            installed.append(
                install_skill(
                    skill_name=skill_name,
                    source_root=skills_root,
                    destination_root=destination_root,
                    mode=args.mode,
                    force=args.force,
                )
            )

        print(f"repo: {repo_root}")
        print(f"project: {project_root}")
        print(f"mode: {args.mode}")
        print("installed:")
        for path in installed:
            print(f"  - {path}")
        print("next: run optional harness links with `agentskills link` if needed.")
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
