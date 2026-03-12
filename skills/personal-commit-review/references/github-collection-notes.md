# GitHub Collection Notes

Open this file when the GitHub collection step needs debugging, tuning, or a trustworthiness check.

## Collection Strategy

1. Discover touched repositories from GitHub GraphQL:
   `viewer { contributionsCollection(from:, to:) { totalCommitContributions restrictedContributionsCount commitContributionsByRepository(maxRepositories:) { repository { ... } } } }`
2. Fetch commit summaries per discovered repository through REST:
   `GET /repos/{owner}/{repo}/commits?author=<login>&since=<iso>&until=<iso>`
3. Fetch detailed commit payloads only for a bounded highlight sample:
   `GET /repos/{owner}/{repo}/commits/{sha}`

This split gives enough evidence to write a specific narrative without forcing the agent to inspect every commit one by one.

Use manual `gh` queries by default when the review is small. Use the helper script when the repo count or date range makes manual collection tedious.

## Why This Shape Works

- GraphQL contribution discovery is cheap and gives a user-centric view of activity across public and private repositories they can still access.
- REST commit listing is better for per-commit headlines and stable filtering by `author`, `since`, and `until`.
- Detailed commit payloads are much larger because they include file and stats data, so fetch them only for the strongest story candidates.

## Sharp Edges

- `gh api` switches to `POST` when fields are present unless the method is forced. Always call REST list endpoints with `gh api --method GET ... -f key=value`.
- `gh api user/emails` usually requires the `user` scope. Treat email discovery as optional enrichment, not a hard dependency.
- `restrictedContributionsCount` can be greater than zero even for the authenticated viewer. Those contributions count toward totals but do not expose repo-level detail.
- GitHub contribution totals can exceed the number of retrievable commit objects. Branch-only work, squash/merge flows, and other GitHub contribution rules do not always map back to a simple visible commit list.
- If `commitContributionsByRepository(maxRepositories:N)` returns exactly `N` repos, the result may be truncated. Raise the limit before assuming you saw everything.

## Missing-Commit Checklist

- Confirm the date range is correct and in UTC-compatible ISO format.
- Check whether the commit is linked to the user's GitHub account. Login-based author filtering only finds linked contributions.
- Check whether the repository is still accessible to the authenticated account.
- Compare `totalCommitContributions` with the collector's visible commit count. A gap often means restricted, branch-only, squashed, or otherwise unrecoverable contributions, not necessarily a collector bug.
- If the user wants deeper recall for older or unusually attributed commits, ask whether they want to refresh `gh` with broader scopes and rerun.

## Rate Limits

- Authenticated GitHub REST requests normally get 5,000 requests per hour.
- Authenticated GitHub GraphQL requests normally get 5,000 points per hour.
- The collector already keeps GraphQL usage low and limits REST detail fetches, so ordinary weekly or monthly reviews should stay well below those caps.
- If GitHub returns a secondary rate-limit response, back off and retry rather than immediately widening concurrency.

## Useful Follow-Ups

- Reinspect one commit:
  `gh api --method GET repos/OWNER/REPO/commits/SHA`
- Inspect remaining budget:
  `gh api rate_limit`
- Test the GraphQL discovery query manually:
  `gh api graphql -f query='query { viewer { contributionsCollection(from:"2026-03-01T00:00:00Z", to:"2026-03-10T23:59:59Z") { totalCommitContributions restrictedContributionsCount } } }'`

## Official Docs

- GraphQL objects and contribution fields:
  [docs.github.com/en/graphql/reference/objects#contributionscollection](https://docs.github.com/en/graphql/reference/objects#contributionscollection)
- REST commit listing:
  [docs.github.com/en/rest/commits/commits?apiVersion=2022-11-28#list-commits](https://docs.github.com/en/rest/commits/commits?apiVersion=2022-11-28#list-commits)
- REST rate limits:
  [docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api)
- GraphQL rate limits:
  [docs.github.com/en/graphql/overview/rate-limits-and-query-limits-for-the-graphql-api](https://docs.github.com/en/graphql/overview/rate-limits-and-query-limits-for-the-graphql-api)
