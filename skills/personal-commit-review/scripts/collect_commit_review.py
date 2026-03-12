#!/usr/bin/env python3
# ruff: noqa: D101,D102,D103
"""Collect GitHub commit activity for a personal prose review.

This script is designed for agent skills: keep collection deterministic and keep
the large raw payload out of the model context. It uses the authenticated `gh`
CLI for both GraphQL discovery and REST commit lookups.
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

DEFAULT_LOOKBACK_DAYS = 30
DEFAULT_MAX_REPOS = 100
DEFAULT_MAX_COMMITS_PER_REPO = 100
DEFAULT_MAX_DETAILED_COMMITS = 24
DEFAULT_MAX_WORKERS = 6
REQUEST_TIMEOUT = 60
GRAPHQL_QUERY = """
query PersonalCommitReview($from: DateTime!, $to: DateTime!, $maxRepos: Int!) {
  viewer {
    login
    name
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
      }
      commitContributionsByRepository(maxRepositories: $maxRepos) {
        repository {
          nameWithOwner
          isPrivate
          description
          url
          pushedAt
          primaryLanguage {
            name
          }
          languages(first: 5, orderBy: {field: SIZE, direction: DESC}) {
            edges {
              size
              node {
                name
              }
            }
          }
        }
        contributions(first: 10) {
          totalCount
          nodes {
            occurredAt
            commitCount
          }
        }
      }
    }
  }
  rateLimit {
    cost
    remaining
    resetAt
  }
}
""".strip()


@dataclass(slots=True)
class DateRange:
    since: datetime
    until: datetime

    def as_api_strings(self) -> tuple[str, str]:
        return to_github_datetime(self.since), to_github_datetime(self.until)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Collect personal GitHub commit activity and produce a compact brief "
            "for a narrative review."
        )
    )
    parser.add_argument(
        "--since",
        help=(
            "Start date or datetime in ISO-8601 format. Date-only inputs use 00:00:00Z."
        ),
    )
    parser.add_argument(
        "--until",
        help="End date or datetime in ISO-8601 format. Date-only inputs use 23:59:59Z.",
    )
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=DEFAULT_LOOKBACK_DAYS,
        help=(
            "Days to look back when --since is omitted "
            f"(default: {DEFAULT_LOOKBACK_DAYS})."
        ),
    )
    parser.add_argument(
        "--max-repos",
        type=int,
        default=DEFAULT_MAX_REPOS,
        help=(
            "Max repositories to request from GitHub GraphQL "
            f"(default: {DEFAULT_MAX_REPOS})."
        ),
    )
    parser.add_argument(
        "--max-commits-per-repo",
        type=int,
        default=DEFAULT_MAX_COMMITS_PER_REPO,
        help=(
            "Max commit summaries to collect per repository through the REST API "
            f"(default: {DEFAULT_MAX_COMMITS_PER_REPO})."
        ),
    )
    parser.add_argument(
        "--max-detailed-commits",
        type=int,
        default=DEFAULT_MAX_DETAILED_COMMITS,
        help=(
            "Max commit detail payloads to fetch across all repositories "
            f"(default: {DEFAULT_MAX_DETAILED_COMMITS})."
        ),
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=DEFAULT_MAX_WORKERS,
        help=(
            "Concurrent GitHub requests for per-repo work "
            f"(default: {DEFAULT_MAX_WORKERS})."
        ),
    )
    parser.add_argument(
        "--output",
        help="Write the structured JSON payload to this file instead of stdout.",
    )
    parser.add_argument(
        "--brief-out",
        help="Write a compact Markdown brief for the agent to read first.",
    )
    return parser.parse_args()


def parse_date_range(args: argparse.Namespace) -> DateRange:
    if args.since:
        since = parse_user_datetime(args.since, end_of_day=False)
    else:
        since = datetime.now(UTC) - timedelta(days=args.lookback_days)
        since = since.replace(hour=0, minute=0, second=0, microsecond=0)

    if args.until:
        until = parse_user_datetime(args.until, end_of_day=True)
    else:
        until = datetime.now(UTC)

    if until < since:
        raise ValueError("--until must be after --since")

    return DateRange(since=since, until=until)


def parse_user_datetime(value: str, *, end_of_day: bool) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"

    if "T" not in value:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        else:
            parsed = parsed.astimezone(UTC)
        if end_of_day:
            return parsed.replace(hour=23, minute=59, second=59, microsecond=0)
        return parsed.replace(hour=0, minute=0, second=0, microsecond=0)

    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def to_github_datetime(value: datetime) -> str:
    return (
        value.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    )


def run_json_command(cmd: list[str], *, timeout: int = REQUEST_TIMEOUT) -> Any:
    attempts = 0
    while True:
        attempts += 1
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)

        stderr = result.stderr.strip()
        if attempts < 4 and should_retry(stderr):
            time.sleep(2 ** (attempts - 1))
            continue

        raise RuntimeError(
            stderr or result.stdout.strip() or "GitHub CLI request failed"
        )


def should_retry(stderr: str) -> bool:
    lowered = stderr.lower()
    return "secondary rate limit" in lowered or "rate limit exceeded" in lowered


def gh_graphql(query: str, **variables: Any) -> Any:
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        if isinstance(value, bool):
            cmd.extend(["-F", f"{key}={str(value).lower()}"])
        else:
            cmd.extend(["-F", f"{key}={value}"])
    return run_json_command(cmd)


def gh_rest(path: str, **params: Any) -> Any:
    cmd = ["gh", "api", "--method", "GET", path]
    for key, value in params.items():
        cmd.extend(["-f", f"{key}={value}"])
    return run_json_command(cmd)


def ensure_gh_ready() -> None:
    try:
        subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=15,
            check=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("`gh` is required but was not found on PATH.") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            "GitHub CLI is installed but not authenticated. Run `gh auth status`."
        ) from exc


def fetch_viewer_contributions(date_range: DateRange, max_repos: int) -> dict[str, Any]:
    since, until = date_range.as_api_strings()
    payload = gh_graphql(
        GRAPHQL_QUERY,
        **{
            "from": since,
            "to": until,
            "maxRepos": max_repos,
        },
    )
    return payload["data"]


def summarize_language_edges(edges: list[dict[str, Any]]) -> dict[str, int]:
    languages: dict[str, int] = {}
    for edge in edges:
        node = edge.get("node") or {}
        name = node.get("name")
        size = edge.get("size")
        if name and isinstance(size, int):
            languages[name] = size
    return languages


def list_repo_commits(
    repo_name: str,
    author: str,
    date_range: DateRange,
    *,
    max_commits: int,
) -> dict[str, Any]:
    since, until = date_range.as_api_strings()
    commits: list[dict[str, Any]] = []
    page = 1
    truncated = False

    while len(commits) < max_commits:
        remaining = max_commits - len(commits)
        per_page = min(100, remaining)
        page_items = gh_rest(
            f"repos/{repo_name}/commits",
            author=author,
            since=since,
            until=until,
            per_page=per_page,
            page=page,
        )
        if not page_items:
            break

        for item in page_items:
            message = ((item.get("commit") or {}).get("message")) or ""
            author_block = item.get("author") or {}
            committer_block = item.get("committer") or {}
            commit_block = item.get("commit") or {}
            commit_author = commit_block.get("author") or {}
            commit_committer = commit_block.get("committer") or {}

            commits.append(
                {
                    "sha": item.get("sha"),
                    "html_url": item.get("html_url"),
                    "date": commit_author.get("date") or commit_committer.get("date"),
                    "headline": message.splitlines()[0].strip() if message else "",
                    "message": message,
                    "author_login": author_block.get("login"),
                    "committer_login": committer_block.get("login"),
                    "is_merge": len(item.get("parents") or []) > 1
                    or message.startswith("Merge "),
                }
            )
            if len(commits) >= max_commits:
                break

        if len(page_items) < per_page:
            break
        if len(commits) >= max_commits:
            truncated = True
            break
        page += 1

    return {"commits": commits, "truncated": truncated}


def pick_detail_targets(
    repo_entries: list[dict[str, Any]], max_detailed_commits: int
) -> list[tuple[str, str]]:
    if max_detailed_commits <= 0:
        return []

    scored: list[tuple[float, str, str]] = []
    per_repo_picks = max(1, math.ceil(max_detailed_commits / max(1, len(repo_entries))))

    for repo in repo_entries:
        repo_name = repo["name_with_owner"]
        repo_commits = repo["commits"]
        ranked = sorted(
            repo_commits,
            key=lambda item: score_commit_summary(item["message"]),
            reverse=True,
        )
        for item in ranked[:per_repo_picks]:
            scored.append(
                (score_commit_summary(item["message"]), repo_name, item["sha"])
            )

    seen: set[tuple[str, str]] = set()
    ordered: list[tuple[str, str]] = []
    for _score, repo_name, sha in sorted(scored, reverse=True):
        key = (repo_name, sha)
        if key in seen:
            continue
        seen.add(key)
        ordered.append(key)
        if len(ordered) >= max_detailed_commits:
            break

    return ordered


def score_commit_summary(message: str) -> float:
    headline = (message.splitlines()[0] if message else "").strip().lower()
    score = 0.0
    if len(headline) >= 18:
        score += 1.0
    if len(message.splitlines()) > 1:
        score += 1.5

    keyword_weights = {
        "liquid glass": 4.0,
        "hig": 4.0,
        "swiftui": 3.0,
        "design": 2.5,
        "redesign": 3.5,
        "settings": 1.0,
        "window": 1.0,
        "feature": 2.0,
        "support": 1.5,
        "refactor": 2.0,
        "rewrite": 2.0,
        "release": 1.5,
        "sign": 1.0,
        "signing": 2.0,
        "build": 1.0,
        "packag": 1.0,
        "test": 1.0,
        "fix": 1.0,
        "bug": 1.0,
        "performance": 2.0,
        "migrate": 2.0,
        "review": 1.0,
    }
    for token, weight in keyword_weights.items():
        if token in headline:
            score += weight

    boring_prefixes = (
        "bump version",
        "chore:",
        "merge branch",
        "merge remote-tracking branch",
        "typo",
        "format",
    )
    if headline.startswith(boring_prefixes):
        score -= 1.5

    return score


def fetch_commit_detail(repo_name: str, sha: str) -> dict[str, Any]:
    item = gh_rest(f"repos/{repo_name}/commits/{sha}")
    stats = item.get("stats") or {}
    files = item.get("files") or []
    trimmed_files = [
        {
            "filename": file_item.get("filename"),
            "status": file_item.get("status"),
            "additions": file_item.get("additions"),
            "deletions": file_item.get("deletions"),
            "changes": file_item.get("changes"),
        }
        for file_item in files[:20]
    ]

    return {
        "sha": item.get("sha"),
        "stats": {
            "additions": stats.get("additions", 0),
            "deletions": stats.get("deletions", 0),
            "total": stats.get("total", 0),
        },
        "changed_files": len(files),
        "files": trimmed_files,
    }


def detect_tags(text: str) -> list[str]:
    lowered = text.lower()
    patterns = {
        "liquid-glass": ("liquid glass",),
        "hig": ("hig", "human interface guideline"),
        "release": ("release", "version", "signing", "dmg"),
        "design": ("design", "redesign", "ui", "window", "toolbar", "sidebar"),
        "refactor": ("refactor", "rewrite", "cleanup", "decoupl"),
        "tests": ("test", "pytest", "coverage"),
        "docs": ("docs", "readme", "guide", "reference"),
        "build": ("build", "workflow", "ci", "package", "brew", "tap"),
        "bugfix": ("fix", "bug", "crash", "error", "regression"),
    }
    matches = [
        name
        for name, needles in patterns.items()
        if any(needle in lowered for needle in needles)
    ]
    return sorted(matches)


def attach_details(
    repo_entries: list[dict[str, Any]],
    detail_targets: list[tuple[str, str]],
    max_workers: int,
) -> None:
    repo_lookup = {repo["name_with_owner"]: repo for repo in repo_entries}
    futures = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for repo_name, sha in detail_targets:
            futures[executor.submit(fetch_commit_detail, repo_name, sha)] = (
                repo_name,
                sha,
            )

        for future in as_completed(futures):
            repo_name, sha = futures[future]
            try:
                detail = future.result()
            except (
                Exception
            ) as exc:  # pragma: no cover - exercised by live API failure paths.
                repo_lookup[repo_name]["errors"].append(f"detail {sha[:7]}: {exc}")
                continue

            repo = repo_lookup[repo_name]
            repo["detail_by_sha"][sha] = detail

    for repo in repo_entries:
        top_files = Counter()
        additions = 0
        deletions = 0
        changed_files = 0

        for commit in repo["commits"]:
            detail = repo["detail_by_sha"].get(commit["sha"])
            if not detail:
                continue
            commit["detail"] = detail
            stat_block = detail["stats"]
            additions += stat_block["additions"]
            deletions += stat_block["deletions"]
            changed_files += detail["changed_files"]
            commit["tags"] = detect_tags(
                commit["message"]
                + "\n"
                + " ".join(file_item["filename"] or "" for file_item in detail["files"])
            )
            commit["highlight_score"] = score_commit_summary(commit["message"]) + min(
                6.0,
                detail["changed_files"] / 3 + stat_block["total"] / 120,
            )
            for file_item in detail["files"]:
                if file_item["filename"]:
                    top_files[file_item["filename"]] += 1

        repo["detail_summary"] = {
            "sampled_additions": additions,
            "sampled_deletions": deletions,
            "sampled_changed_files": changed_files,
            "sampled_commit_details": len(repo["detail_by_sha"]),
            "top_files": [
                {"path": path, "touches": count}
                for path, count in top_files.most_common(8)
            ],
        }


def build_repo_entry(
    repo_block: dict[str, Any], active_days: dict[str, Any]
) -> dict[str, Any]:
    repository = repo_block["repository"]
    languages = summarize_language_edges(
        ((repository.get("languages") or {}).get("edges")) or []
    )
    preview_days = [
        {
            "occurred_at": node.get("occurredAt"),
            "commit_count": node.get("commitCount"),
        }
        for node in ((active_days.get("nodes")) or [])
    ]
    return {
        "name_with_owner": repository["nameWithOwner"],
        "is_private": repository["isPrivate"],
        "description": repository.get("description"),
        "url": repository.get("url"),
        "pushed_at": repository.get("pushedAt"),
        "primary_language": ((repository.get("primaryLanguage") or {}).get("name")),
        "languages": languages,
        "active_day_count": active_days.get("totalCount", 0),
        "activity_preview": preview_days,
        "commits": [],
        "detail_by_sha": {},
        "detail_summary": {},
        "errors": [],
        "commit_collection_truncated": False,
    }


def collect_repo_data(
    repo_entries: list[dict[str, Any]],
    author: str,
    date_range: DateRange,
    max_commits_per_repo: int,
    max_workers: int,
) -> None:
    futures = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for repo in repo_entries:
            futures[
                executor.submit(
                    list_repo_commits,
                    repo["name_with_owner"],
                    author,
                    date_range,
                    max_commits=max_commits_per_repo,
                )
            ] = repo

        for future in as_completed(futures):
            repo = futures[future]
            try:
                collected = future.result()
            except (
                Exception
            ) as exc:  # pragma: no cover - exercised by live API failure paths.
                repo["errors"].append(f"commit list: {exc}")
                continue
            repo["commits"] = collected["commits"]
            repo["commit_collection_truncated"] = collected["truncated"]


def finalize_repo_entries(repo_entries: list[dict[str, Any]]) -> None:
    for repo in repo_entries:
        repo["accessible_commit_count"] = len(repo["commits"])
        repo["highlight_candidates"] = [
            {
                "sha": commit["sha"],
                "headline": commit["headline"],
                "date": commit["date"],
                "tags": commit.get("tags", detect_tags(commit["message"])),
                "score": round(
                    commit.get(
                        "highlight_score", score_commit_summary(commit["message"])
                    ),
                    2,
                ),
                "html_url": commit["html_url"],
            }
            for commit in sorted(
                repo["commits"],
                key=lambda item: item.get(
                    "highlight_score", score_commit_summary(item["message"])
                ),
                reverse=True,
            )[:4]
        ]

        repo["commits"] = [
            {
                "sha": commit["sha"],
                "date": commit["date"],
                "headline": commit["headline"],
                "message": commit["message"],
                "html_url": commit["html_url"],
                "author_login": commit["author_login"],
                "committer_login": commit["committer_login"],
                "is_merge": commit["is_merge"],
                "tags": commit.get("tags", detect_tags(commit["message"])),
                "detail": commit.get("detail"),
            }
            for commit in repo["commits"]
        ]
        repo.pop("detail_by_sha", None)


def aggregate_totals(
    repo_entries: list[dict[str, Any]],
    total_commit_contributions: int,
    restricted_contributions_count: int,
) -> dict[str, Any]:
    accessible_commit_count = sum(
        repo["accessible_commit_count"] for repo in repo_entries
    )
    accessible_commit_count_is_lower_bound = any(
        repo["commit_collection_truncated"] for repo in repo_entries
    )
    private_repo_count = sum(1 for repo in repo_entries if repo["is_private"])
    public_repo_count = sum(1 for repo in repo_entries if not repo["is_private"])

    language_totals = Counter()
    activity_by_day = Counter()
    for repo in repo_entries:
        language_totals.update(repo["languages"])
        for commit in repo["commits"]:
            if commit["date"]:
                activity_by_day[commit["date"][:10]] += 1

    unmatched_count = max(
        total_commit_contributions - accessible_commit_count,
        restricted_contributions_count,
    )
    top_languages = []
    language_total_bytes = sum(language_totals.values())
    for name, size in language_totals.most_common(8):
        share = (
            round(size / language_total_bytes * 100, 1) if language_total_bytes else 0.0
        )
        top_languages.append({"name": name, "bytes": size, "share_percent": share})

    busiest_day = None
    if activity_by_day:
        date, count = activity_by_day.most_common(1)[0]
        busiest_day = {"date": date, "accessible_commit_count": count}

    return {
        "repo_count": len(repo_entries),
        "public_repo_count": public_repo_count,
        "private_repo_count": private_repo_count,
        "total_commit_contributions": total_commit_contributions,
        "restricted_contributions_count": restricted_contributions_count,
        "accessible_commit_count": accessible_commit_count,
        "accessible_commit_count_is_lower_bound": (
            accessible_commit_count_is_lower_bound
        ),
        "unmatched_commit_count": unmatched_count,
        "unmatched_commit_count_is_upper_bound": accessible_commit_count_is_lower_bound,
        "top_languages": top_languages,
        "busiest_day": busiest_day,
    }


def build_highlight_index(repo_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    highlights: list[dict[str, Any]] = []
    for repo in repo_entries:
        for candidate in repo["highlight_candidates"]:
            highlights.append(
                {
                    "repo": repo["name_with_owner"],
                    "primary_language": repo["primary_language"],
                    "is_private": repo["is_private"],
                    **candidate,
                }
            )
    highlights.sort(key=lambda item: item["score"], reverse=True)
    return highlights[:12]


def build_limitations(
    *,
    restricted_contributions_count: int,
    total_commit_contributions: int,
    accessible_commit_count: int,
    repo_count: int,
    max_repos: int,
    email_scope_available: bool,
    repo_entries: list[dict[str, Any]],
) -> list[str]:
    limitations: list[str] = []
    if restricted_contributions_count:
        limitations.append(
            f"GitHub reports {restricted_contributions_count} restricted "
            "contribution(s) in this window. "
            "They count toward totals but cannot be mapped to accessible repo details."
        )
    if total_commit_contributions > accessible_commit_count:
        limitations.append(
            "GitHub contribution totals can exceed retrievable commit objects. "
            "Branch-only, squashed, or otherwise unrecoverable contributions may "
            "still count in the contribution graph."
        )
    if repo_count >= max_repos:
        limitations.append(
            "Repository discovery hit the configured GitHub GraphQL max-repos ceiling. "
            "Increase --max-repos if you expect activity in more repositories."
        )
    if not email_scope_available:
        limitations.append(
            "Linked commit emails were not enumerated because the current gh "
            "token does not have the `user` scope. Commit discovery used the "
            "GitHub login, which is usually correct for linked contributions."
        )
    truncated_repos = [
        repo["name_with_owner"]
        for repo in repo_entries
        if repo["commit_collection_truncated"]
    ]
    if truncated_repos:
        limitations.append(
            "Commit collection hit the per-repo summary cap for: "
            + ", ".join(truncated_repos)
            + ". Increase --max-commits-per-repo for a fuller accessible commit sample."
        )
    for repo in repo_entries:
        if repo["errors"]:
            limitations.append(
                f"{repo['name_with_owner']}: {'; '.join(repo['errors'])}"
            )
    return limitations


def write_output(path: str | None, content: str) -> None:
    if path:
        target = Path(path).expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    else:
        print(content)


def maybe_check_email_scope() -> bool:
    result = subprocess.run(
        ["gh", "api", "user/emails"],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    return result.returncode == 0


def build_brief(payload: dict[str, Any]) -> str:
    totals = payload["totals"]
    lines = [
        f"# Commit Review Brief for {payload['viewer']['login']}",
        "",
        f"Period: {payload['range']['since']} to {payload['range']['until']}",
        "",
        "## At a Glance",
        (
            f"- GitHub reports {totals['total_commit_contributions']} commit "
            "contribution(s) "
            f"across {totals['repo_count']} accessible repo(s)."
        ),
        (
            f"- Visible commit summaries collected from repo commit endpoints: "
            f"{totals['accessible_commit_count']} "
            f"({totals['public_repo_count']} public repo(s), "
            f"{totals['private_repo_count']} private repo(s))."
        ),
    ]
    if totals["accessible_commit_count_is_lower_bound"]:
        lines.append(
            "- The collected accessible commit count is a lower bound because "
            "at least one repo hit the per-repo summary cap."
        )
    if totals["unmatched_commit_count"]:
        if totals["unmatched_commit_count_is_upper_bound"]:
            lines.append(
                f"- Up to {totals['unmatched_commit_count']} contributions may "
                "sit outside the visible repo-level commit sample."
            )
        else:
            lines.append(
                "- Contributions not recoverable as visible repo-level commit "
                "objects: "
                f"{totals['unmatched_commit_count']}."
            )
    if totals["busiest_day"]:
        busiest_day = totals["busiest_day"]
        lines.append(
            f"- Busiest accessible day: {busiest_day['date']} with "
            f"{busiest_day['accessible_commit_count']} commit(s)."
        )
    if totals["top_languages"]:
        language_preview = ", ".join(
            f"{item['name']} ({item['share_percent']}%)"
            for item in totals["top_languages"][:5]
        )
        lines.append(f"- Dominant repo languages: {language_preview}.")

    lines.extend(["", "## Potential Story Beats"])
    if payload["highlight_candidates"]:
        for item in payload["highlight_candidates"][:8]:
            tag_text = ", ".join(item["tags"]) if item["tags"] else "general"
            lines.append(
                f"- `{item['repo']}`: {item['headline']} "
                f"({item['date'][:10] if item['date'] else 'undated'}, "
                f"tags: {tag_text})"
            )
    else:
        lines.append("- No strong highlight candidates were automatically detected.")

    lines.extend(["", "## Repo Capsules"])
    for repo in payload["repos"]:
        visibility = "private" if repo["is_private"] else "public"
        lines.extend(
            [
                f"### `{repo['name_with_owner']}`",
                f"- Visibility: {visibility}",
            ]
        )
        if repo["description"]:
            lines.append(f"- Description: {repo['description']}")
        lines.append(
            f"- Visible commits collected: {repo['accessible_commit_count']}"
        )
        if repo["primary_language"]:
            lines.append(f"- Primary language: {repo['primary_language']}")
        if repo["highlight_candidates"]:
            lines.append("- Candidate highlights:")
            for item in repo["highlight_candidates"][:3]:
                lines.append(f"  - {item['headline']} ({item['sha'][:7]})")
        if repo["detail_summary"].get("top_files"):
            file_preview = ", ".join(
                file_item["path"]
                for file_item in repo["detail_summary"]["top_files"][:4]
            )
            lines.append(f"- Frequently touched sampled files: {file_preview}")
        lines.append("")

    if payload["limitations"]:
        lines.extend(["## Caveats"])
        for item in payload["limitations"]:
            lines.append(f"- {item}")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    try:
        args = parse_args()
        date_range = parse_date_range(args)
        ensure_gh_ready()

        graph = fetch_viewer_contributions(date_range, args.max_repos)
        viewer = graph["viewer"]
        collection = viewer["contributionsCollection"]
        rate_limit = graph["rateLimit"]

        repo_entries = [
            build_repo_entry(repo_block, repo_block["contributions"])
            for repo_block in collection["commitContributionsByRepository"]
        ]
        collect_repo_data(
            repo_entries,
            viewer["login"],
            date_range,
            args.max_commits_per_repo,
            max(1, args.max_workers),
        )

        detail_targets = pick_detail_targets(repo_entries, args.max_detailed_commits)
        attach_details(repo_entries, detail_targets, max(1, args.max_workers))
        finalize_repo_entries(repo_entries)

        email_scope_available = maybe_check_email_scope()
        totals = aggregate_totals(
            repo_entries,
            collection["totalCommitContributions"],
            collection["restrictedContributionsCount"],
        )
        limitations = build_limitations(
            restricted_contributions_count=collection["restrictedContributionsCount"],
            total_commit_contributions=collection["totalCommitContributions"],
            accessible_commit_count=totals["accessible_commit_count"],
            repo_count=len(repo_entries),
            max_repos=args.max_repos,
            email_scope_available=email_scope_available,
            repo_entries=repo_entries,
        )

        payload = {
            "generated_at": to_github_datetime(datetime.now(UTC)),
            "viewer": {
                "login": viewer["login"],
                "name": viewer.get("name"),
            },
            "range": {
                "since": to_github_datetime(date_range.since),
                "until": to_github_datetime(date_range.until),
            },
            "totals": totals,
            "highlight_candidates": build_highlight_index(repo_entries),
            "repos": repo_entries,
            "limitations": limitations,
            "source": {
                "gh_cli_required": True,
                "github_graphql_rate_limit": {
                    "cost": rate_limit["cost"],
                    "remaining": rate_limit["remaining"],
                    "reset_at": rate_limit["resetAt"],
                },
                "author_matching": {
                    "mode": "github-login",
                    "email_scope_available": email_scope_available,
                },
            },
        }

        json_output = json.dumps(payload, indent=2, sort_keys=True)
        write_output(args.output, json_output)
        if args.brief_out:
            write_output(args.brief_out, build_brief(payload))
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
