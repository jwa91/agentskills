#!/usr/bin/env python3
"""Scan a macOS dev machine for reclaimable disk space.

Usage:
    python3 .agents/skills/mac-cleanup/scripts/scan.py [OPTIONS]

Outputs a JSON report to stdout with sections: disk, package_managers,
caches, dev_artifacts, docker, trash, downloads, errors.

Zero external dependencies — stdlib only.
"""

import argparse
import contextlib
import json
import os
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

SUBPROCESS_TIMEOUT = 15

# Dev artifact directory names and their descriptions.
DEV_ARTIFACT_NAMES = {
    "node_modules": "npm/pnpm/yarn/bun packages",
    ".venv": "Python virtual environment",
    "venv": "Python virtual environment",
    ".next": "Next.js build cache",
    "dist": "Build output",
    "build": "Build output",
    "target": "Rust/Java build output",
    "__pycache__": "Python bytecode cache",
    ".pytest_cache": "Pytest cache",
    ".mypy_cache": "Mypy cache",
    ".ruff_cache": "Ruff cache",
    ".tox": "Tox environments",
}

# Maximum directory depth when scanning for dev artifacts.
MAX_WALK_DEPTH = 6


def run_cmd(cmd, timeout=SUBPROCESS_TIMEOUT):
    """Run a shell command and return (stdout, stderr, returncode).

    Returns (None, error_message, -1) on timeout or other failure.
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=isinstance(cmd, str),
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return None, f"Timed out after {timeout}s", -1
    except Exception as e:
        return None, str(e), -1


def get_dir_size(path):
    """Get total size of a directory in bytes, following no symlinks."""
    total = 0
    try:
        for dirpath, _dirnames, filenames in os.walk(path, followlinks=False):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                with contextlib.suppress(OSError):
                    total += os.lstat(fp).st_size
    except OSError:
        pass
    return total


def human_size(nbytes):
    """Format bytes as a human-readable string."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(nbytes) < 1024:
            return f"{nbytes:.1f} {unit}"
        nbytes /= 1024
    return f"{nbytes:.1f} PB"


def get_mtime_days(path):
    """Return days since last modification of any file under path."""
    try:
        latest = 0
        for dirpath, _dirnames, filenames in os.walk(path, followlinks=False):
            for f in filenames:
                try:
                    mt = os.lstat(os.path.join(dirpath, f)).st_mtime
                    if mt > latest:
                        latest = mt
                except OSError:
                    pass
            # Only check top-level files for speed on large dirs.
            break
        if latest == 0:
            latest = os.stat(path).st_mtime
        return int((time.time() - latest) / 86400)
    except OSError:
        return -1


# --- Scanners ---


def scan_disk():
    """Get overall disk usage via shutil."""
    try:
        usage = shutil.disk_usage("/")
        return {
            "total": human_size(usage.total),
            "used": human_size(usage.used),
            "free": human_size(usage.free),
            "percent_used": round(usage.used / usage.total * 100, 1),
            "total_bytes": usage.total,
            "free_bytes": usage.free,
        }
    except Exception as e:
        return {"error": str(e)}


def scan_arch():
    """Detect CPU architecture."""
    out, _, rc = run_cmd(["uname", "-m"])
    return out if rc == 0 else "unknown"


def scan_tool(name):
    """Check if a CLI tool is installed and return its path."""
    path = shutil.which(name)
    return {"name": name, "installed": path is not None, "path": path}


def scan_package_managers():
    """Detect installed package managers and their cache sizes."""
    tools = [
        "brew", "npm", "pnpm", "yarn", "bun",
        "uv", "pip", "pip3", "cargo", "go",
        "pyenv", "nvm", "rustup",
    ]
    results = {}
    for t in tools:
        info = scan_tool(t)
        if info["installed"]:
            results[t] = info
    return results


def scan_brew_cache():
    """Get Homebrew cache info."""
    info = {"installed": shutil.which("brew") is not None}
    if not info["installed"]:
        return info

    # Cache size.
    out, _, rc = run_cmd(["brew", "--cache"])
    if rc == 0 and os.path.isdir(out):
        size = get_dir_size(out)
        info["cache_path"] = out
        info["cache_size"] = human_size(size)
        info["cache_bytes"] = size

    # Dry-run cleanup.
    out, _, rc = run_cmd(["brew", "cleanup", "--dry-run", "-s"])
    if rc == 0 and out:
        lines = [line for line in out.splitlines() if line.strip()]
        info["cleanup_items"] = len(lines)

    return info


def scan_caches():
    """Scan common cache directories."""
    cache_dirs = {
        "~/Library/Caches": "macOS app caches",
        "~/Library/Logs": "macOS app logs",
        "~/.cache": "User cache (pip, uv, etc.)",
        "~/.npm": "npm cache",
    }

    # Add pnpm store if it exists.
    pnpm_store = Path.home() / "Library" / "pnpm"
    if pnpm_store.exists():
        cache_dirs["~/Library/pnpm"] = "pnpm store"

    results = {}
    for dir_path, description in cache_dirs.items():
        expanded = os.path.expanduser(dir_path)
        if os.path.isdir(expanded):
            size = get_dir_size(expanded)
            results[dir_path] = {
                "description": description,
                "path": expanded,
                "size": human_size(size),
                "bytes": size,
            }

    return results


def scan_cache_breakdown(cache_dir, top_n=10):
    """Get per-subdirectory breakdown of a cache directory."""
    expanded = os.path.expanduser(cache_dir)
    if not os.path.isdir(expanded):
        return []

    entries = []
    try:
        for entry in os.scandir(expanded):
            if entry.is_dir(follow_symlinks=False):
                size = get_dir_size(entry.path)
                if size > 1_000_000:  # Only report > 1 MB.
                    entries.append({
                        "name": entry.name,
                        "size": human_size(size),
                        "bytes": size,
                    })
    except OSError:
        pass

    entries.sort(key=lambda e: e["bytes"], reverse=True)
    return entries[:top_n]


def scan_dev_artifacts(dev_dirs, stale_days, skip_paths):
    """Find stale dev artifacts in development directories."""
    skip_resolved = {os.path.realpath(os.path.expanduser(s)) for s in skip_paths}
    results = []

    for dev_dir in dev_dirs:
        expanded = os.path.expanduser(dev_dir)
        if not os.path.isdir(expanded):
            continue

        for dirpath, dirnames, _filenames in os.walk(expanded, followlinks=False):
            # Enforce max depth.
            depth = dirpath[len(expanded):].count(os.sep)
            if depth >= MAX_WALK_DEPTH:
                dirnames.clear()
                continue

            # Skip protected paths.
            real = os.path.realpath(dirpath)
            if any(real.startswith(s) for s in skip_resolved):
                dirnames.clear()
                continue

            # Check for artifact dirs among children.
            to_prune = []
            for d in dirnames:
                if d in DEV_ARTIFACT_NAMES:
                    full = os.path.join(dirpath, d)
                    real_full = os.path.realpath(full)
                    if any(real_full.startswith(s) for s in skip_resolved):
                        continue

                    age = get_mtime_days(full)
                    size = get_dir_size(full)
                    results.append({
                        "path": full,
                        "type": d,
                        "description": DEV_ARTIFACT_NAMES[d],
                        "size": human_size(size),
                        "bytes": size,
                        "days_since_modified": age,
                        "stale": age >= stale_days,
                    })
                    # Don't recurse into artifact dirs.
                    to_prune.append(d)

            for p in to_prune:
                dirnames.remove(p)

            # Also skip hidden dirs and common non-project dirs.
            dirnames[:] = [
                d for d in dirnames
                if not d.startswith(".") and d not in {"vendor", "Pods"}
            ]

    results.sort(key=lambda e: e["bytes"], reverse=True)
    return results


def scan_docker():
    """Check Docker status and disk usage."""
    info = {"installed": shutil.which("docker") is not None}
    if not info["installed"]:
        return info

    # Check if daemon is running.
    _, _, rc = run_cmd(["docker", "info"], timeout=5)
    info["running"] = rc == 0
    if not info["running"]:
        return info

    out, _, rc = run_cmd(["docker", "system", "df", "--format", "json"])
    if rc == 0 and out:
        try:
            rows = [json.loads(line) for line in out.strip().splitlines()]
            info["usage"] = rows
        except json.JSONDecodeError:
            info["usage_raw"] = out

    return info


def scan_trash():
    """Check Trash size."""
    trash = os.path.expanduser("~/.Trash")
    if os.path.isdir(trash):
        size = get_dir_size(trash)
        return {"path": trash, "size": human_size(size), "bytes": size}
    return {"path": trash, "size": "0 B", "bytes": 0}


def scan_downloads():
    """Check Downloads folder size."""
    downloads = os.path.expanduser("~/Downloads")
    if os.path.isdir(downloads):
        size = get_dir_size(downloads)
        count = sum(1 for _ in os.scandir(downloads))
        return {
            "path": downloads,
            "size": human_size(size),
            "bytes": size,
            "item_count": count,
        }
    return {"path": downloads, "size": "0 B", "bytes": 0, "item_count": 0}


def scan_browsers():
    """Detect browsers installed in /Applications."""
    browsers = [
        "Google Chrome.app",
        "Google Chrome Dev.app",
        "Google Chrome Canary.app",
        "Brave Browser.app",
        "Firefox.app",
        "Microsoft Edge.app",
        "Arc.app",
        "Vivaldi.app",
        "Opera.app",
        "Safari.app",
    ]
    found = []
    for b in browsers:
        path = f"/Applications/{b}"
        if os.path.isdir(path):
            found.append(b.replace(".app", ""))
    return found


def default_dev_dirs():
    """Return sensible default dev directories that exist."""
    candidates = [
        "~/developer",
        "~/Developer",
        "~/dev",
        "~/projects",
        "~/Projects",
        "~/src",
        "~/code",
        "~/Code",
        "~/workspace",
        "~/repos",
        "~/Repos",
    ]
    return [
        c for c in candidates if os.path.isdir(os.path.expanduser(c))
    ]


def main():
    """Run all scans in parallel and output JSON."""
    parser = argparse.ArgumentParser(
        description="Scan macOS dev machine for reclaimable disk space"
    )
    parser.add_argument(
        "--dev-dirs",
        nargs="*",
        default=None,
        help="Directories to scan for dev artifacts (default: auto-detect)",
    )
    parser.add_argument(
        "--stale-days",
        type=int,
        default=90,
        help="Days since last modification to consider stale (default: 90)",
    )
    parser.add_argument(
        "--skip",
        nargs="*",
        default=[],
        help="Paths to skip during dev artifact scan",
    )
    args = parser.parse_args()

    dev_dirs = args.dev_dirs if args.dev_dirs is not None else default_dev_dirs()
    errors = []

    # Define all scan tasks.
    tasks = {
        "disk": scan_disk,
        "arch": scan_arch,
        "package_managers": scan_package_managers,
        "brew": scan_brew_cache,
        "caches": scan_caches,
        "cache_breakdown_library": lambda: scan_cache_breakdown("~/Library/Caches"),
        "cache_breakdown_user": lambda: scan_cache_breakdown("~/.cache"),
        "docker": scan_docker,
        "trash": scan_trash,
        "downloads": scan_downloads,
        "browsers": scan_browsers,
    }

    results = {}
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(fn): name for name, fn in tasks.items()}

        # Dev artifacts scan runs in main thread after quick scans.
        dev_future = pool.submit(
            scan_dev_artifacts, dev_dirs, args.stale_days, args.skip
        )
        futures[dev_future] = "dev_artifacts"

        for future in as_completed(futures):
            name = futures[future]
            try:
                results[name] = future.result()
            except Exception as e:
                errors.append({"scan": name, "error": str(e)})

    # Assemble final report.
    report = {
        "disk": results.get("disk", {}),
        "arch": results.get("arch", "unknown"),
        "package_managers": results.get("package_managers", {}),
        "brew": results.get("brew", {}),
        "caches": results.get("caches", {}),
        "cache_breakdown": {
            "~/Library/Caches": results.get("cache_breakdown_library", []),
            "~/.cache": results.get("cache_breakdown_user", []),
        },
        "dev_artifacts": results.get("dev_artifacts", []),
        "dev_dirs_scanned": dev_dirs,
        "stale_threshold_days": args.stale_days,
        "docker": results.get("docker", {}),
        "trash": results.get("trash", {}),
        "downloads": results.get("downloads", {}),
        "browsers": results.get("browsers", []),
        "errors": errors,
    }

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
