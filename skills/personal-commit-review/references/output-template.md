# Weekly Commit Review: <date range>

Write the whole document at about one page total. Usually 450-750 words is enough.

Do not collapse this into plain paragraphs only. Always keep the report structure below.

## Required Shape

```md
# Weekly Commit Review: March 4-10, 2026

> A one-line deck that captures the week's overall direction.

## At a Glance

| Metric | Value |
| --- | --- |
| Commit contributions | 147 |
| Visible commits inspected | 90 |
| Repos touched | 3 |
| Public / Private | 2 / 1 |
| Dominant languages | Swift, Ruby |

## Repository Footprint

| Repo | Visibility | Role This Week | Language |
| --- | --- | --- | --- |
| [jwa91/trnscrb](https://github.com/jwa91/trnscrb) | Public | Product and UX work | Swift |
| [jwa91/private-repo](https://github.com/jwa91/private-repo) | Private | Internal tooling | TypeScript |

## Narrative

### Main Thread

One paragraph.

### Secondary Thread

One paragraph.

## Linked Highlights

- [Repo or commit link](https://example.com): one sentence on why it mattered.
- [Repo or commit link](https://example.com): one sentence on why it mattered.

## Caveat

One or two sentences only when needed.
```

## Opening Deck

Write one sharp line under the title.

- This should feel like the subheading of a report, not filler.
- Mention the main direction of the week, not every theme.

## At a Glance

Always include a compact stats table. Prefer these rows:

- Commit contributions
- Visible commits inspected
- Repos touched
- Public / Private
- Dominant languages
- Restricted contributions, only if non-zero

## Repository Footprint

Always include a repo table if you have at least one repo.

- Link repo names with Markdown links when URLs are known.
- Include private repo links too if the authenticated query surfaced them and the report is clearly for the same user.
- If GitHub only exposed restricted contributions and not the repo identity, do not invent a repo row.
- Keep the "Role This Week" cell short and useful.

## Narrative

Write 2 sections in most cases.

### Main Thread

Write one paragraph about the most important stream of work.

- Name the repo and link it if that reads naturally.
- Explain what area of the product or system it affects.
- Explain what changed and why it matters.

### Secondary Thread

Write one paragraph about the next most important theme.

- This can be another repo or another kind of work in the same repo.
- Good examples: release engineering, testing, packaging, developer tooling, architectural cleanup.

## Linked Highlights

Include 2-4 compact bullets.

- These bullets are evidence, not the main story.
- Prefer commit links for especially concrete changes.
- Prefer repo links when the highlight is really a stream of work rather than one commit.
- Keep each bullet to one sentence.

## Caveat

Only include this section if needed.

Write 1-2 sentences if:

- GitHub reported restricted contributions
- contribution totals exceed visible commit objects
- some repos were inaccessible
- attribution is uncertain
