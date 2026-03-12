---
name: personal-commit-review
description: "Create a personal GitHub coding retrospective from a date range and turn it into a short Markdown review. Research commit activity across accessible public and private repositories through the authenticated gh CLI, understand what the relevant repositories and subsystems are for, and write a prose retrospective with stats and highlights. Use when the user asks for a commit review, coding recap, engineering retrospective, GitHub activity story, weekly/monthly/yearly highlights, or a written summary of what their commits achieved."
metadata:
  version: 0.1.0
---

# Personal Commit Review

Write a short Markdown retrospective of a person's GitHub work. Make it read like a written review, not a changelog and not a bullet-only summary.

## Default Behavior

- If the user does not specify a time period, default to the last 7 days and say so plainly.
- Default deliverable: one Markdown note, about one page total, usually 400-700 words.
- Use scripts only when they materially help. This skill is primarily a workflow for gathering evidence and writing well.

## Workflow

### 1. Set the review window

- If the period is ambiguous, ask once. If asking would only slow down an otherwise straightforward request, default to the last 7 days and state the assumption.
- Prefer exact `--since` and `--until` dates for weekly, monthly, quarterly, or release reviews.
- Decide whether the user wants the review only in chat or also written to a Markdown file.

### 2. Gather the contribution map

- Start with GitHub totals and the touched repositories. This gives the frame of the review before you study individual commits.
- Manual `gh` usage is fine for v1 and should be the default for small review windows or a small number of repos.
- Use the helper script only when the time window or repo count makes manual collection annoying.

```bash
gh api graphql -f query='query {
  viewer {
    login
    contributionsCollection(from:"2026-03-01T00:00:00Z", to:"2026-03-07T23:59:59Z") {
      totalCommitContributions
      restrictedContributionsCount
      commitContributionsByRepository(maxRepositories:25) {
        repository {
          nameWithOwner
          description
          isPrivate
          url
          primaryLanguage { name }
        }
        contributions(first:7) {
          nodes { occurredAt commitCount }
        }
      }
    }
  }
}'
```

- If you want the helper path, use:

```bash
uv run .agents/skills/personal-commit-review/scripts/collect_commit_review.py \
  --since 2026-03-01 \
  --until 2026-03-07 \
  --output /tmp/commit-review.json \
  --brief-out /tmp/commit-review-brief.md
```

- Treat GitHub's contribution totals as authoritative counts and the retrieved commit objects as the visible research set.
- Open [github-collection-notes.md](references/github-collection-notes.md) when the data looks incomplete or the GitHub queries need adjustment.

### 3. Understand the repos before interpreting the commits

- Do not infer meaning from commit messages alone.
- For each repo that looks important, gather the minimum context needed to understand what the work was for:
  - repo description and primary language
  - README, architecture note, or docs if the repo has them
  - touched file paths and folder names
  - one or two neighboring commits if a headline is too vague
- Prefer understanding the product or subsystem before writing about what changed in it.

Useful commands:

```bash
gh repo view OWNER/REPO --json nameWithOwner,description,primaryLanguage,url
gh api --method GET repos/OWNER/REPO/commits -f author=USERNAME -f since=2026-03-01T00:00:00Z -f until=2026-03-07T23:59:59Z -f per_page=20
gh api --method GET repos/OWNER/REPO/commits/SHA
```

- Example: if a commit mentions Liquid Glass, verify whether the repo is a macOS app, which window or settings files changed, and whether the repo context supports that description.
- If the repo context is still unclear, describe the change more conservatively.

### 4. Pick the storylines

- Pick 2-4 themes for the review, not 10 separate commit bullets.
- Good themes are usually product-facing or architectural:
  - interface polish and design alignment
  - release and packaging work
  - infrastructure or tooling improvements
  - a feature thread that moved from idea to working implementation
- Support each theme with concrete evidence from commits, repo context, and changed paths.

### 5. Parallelize research when it actually helps

- If the review spans many repos or many strong highlights, split follow-up work by repo or theme.
- Give each subagent exclusive ownership of specific repos or highlight commits.
- Do not have every subagent repeat the full discovery step.
- Keep the main agent responsible for the final narrative voice and the final fact check.

### 6. Write the review as prose

- Use the default structure in [output-template.md](references/output-template.md).
- Do not return a wall of paragraphs. The final Markdown should read like a compact report.
- Start with a short framing paragraph that includes the key stats: commit count, repo count, major languages, and any caveat that materially changes interpretation.
- Include a small stats overview table near the top.
- Include a repository overview table with Markdown links to the repos when GitHub exposed the repo URLs.
- Then write 2-3 short body sections that tell the story of the week.
- Name specific repos and changes inside the prose. Example style: "`trnscrb` moved closer to native macOS conventions, with settings-window work explicitly calling out HIG and Liquid Glass patterns."
- Mention 3-5 standout changes, but weave them into the text instead of turning them into a checklist.
- Include 2-4 linked highlights near the end, pointing to repos or commits where that helps the report feel concrete.
- Keep the whole review to about one page total.
- End with one compact caveat note only if needed: restricted contributions, incomplete visibility, inaccessible repos, or uncertain attribution.

## Troubleshooting

- Only verify GitHub access if the data collection step fails or returns clearly wrong results.

```bash
gh auth status
gh api rate_limit
```

- Do not require extra GitHub scopes by default.
- Open [github-collection-notes.md](references/github-collection-notes.md) if the contribution totals and visible commit set do not line up cleanly.

## Output Standard

- Prefer Markdown if writing to a file.
- Keep the tone reflective and concrete.
- Use stats to anchor the story, not to dominate it.
- Use report structure: heading, one-line deck, stats table, repository table, prose sections, compact highlights.
- Link repo names with standard Markdown links whenever the repo URL is known, including private repos that were explicitly surfaced by the authenticated GitHub query.
- Avoid raw commit dumps, long bullet lists, or one-sentence-per-commit writing.
- Avoid filling the whole page with caveats. The caveat note should stay short unless the data is genuinely unusable.

## Anti-Patterns

- Do not treat the helper script as mandatory.
- Do not brute-force every accessible repository when a few repos clearly dominate the review.
- Do not claim details for restricted contributions. Say they exist, not what they were.
- Do not require `gh auth refresh -s user` unless the user explicitly wants deeper email-based matching.
- Do not write from commit headlines alone if the repo context is available.
- Do not paste raw JSON or raw API dumps into the final review.
- Do not omit repo links and stats when the data is available.

## Resources

- [references/output-template.md](references/output-template.md)
  Default Markdown structure for the final review.
- `scripts/collect_commit_review.py`
  Optional helper for broad repo discovery and compact briefing when manual collection is too slow.
- [references/github-collection-notes.md](references/github-collection-notes.md)
  Open when debugging data gaps, tuning limits, or changing the GitHub collection strategy.
