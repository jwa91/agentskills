---
name: release
description: Release the current project to the personal Homebrew tap from repo-local release config. Use when the user says "release", "ship", "cut a version", "publish", "make a new tag", or asks how to make a new version available via jwa91/tap.
---

# Release This Project

This project publishes to the personal Homebrew tap at `jwa91/tap`. The release path is determined by repo-local config, not by project name.

## Detect the release path

From the repo root:

- If `.goreleaser.yaml` exists, this is a GoReleaser-owned project. Release with:

```bash
jwa-harden run -- goreleaser release --clean
```

- If `scripts/release.sh` exists, this is a `jwa-tobrew` script-owned cask or formula project. Release with:

```bash
jwa-harden run -- ./scripts/release.sh <version> <path/to/artifact>
```

- If neither file exists, do not invent a release path. Run `jwa-tobrew init --kind=go|cask|formula` first, or inspect the repo docs for a project-specific release process.

If both files exist, prefer `.goreleaser.yaml` for Go projects and treat the script as legacy unless current repo docs say otherwise.

## Preconditions

- Work from a clean git tree on the commit that should be released.
- Confirm the intended semver tag (`vX.Y.Z`) and release notes from recent commits.
- Run the project's normal tests before publishing.
- Run `jwa-tobrew lint` when the repo participates in the `jwa-*` family policy.
- `jwa-harden doctor` should pass.
- For signed macOS releases, run `jwa-harden doctor signing`.

## GoReleaser projects

Use this path when `.goreleaser.yaml` is present. GoReleaser builds the artifacts, creates or updates the GitHub Release, and writes the generated `Casks/<name>.rb` entry back to `jwa91/tap`.

Typical local flow:

```bash
git tag -a vX.Y.Z -m vX.Y.Z
git push origin vX.Y.Z
jwa-harden run -- goreleaser release --clean
```

If the repo has CI wired for tag releases, pushing the tag may be enough. Check the repo's `.github/workflows/` before also running a local release.

## Script-owned cask or formula projects

Use this path when `scripts/release.sh` is present and `.goreleaser.yaml` is absent. The script wraps `jwa-tobrew release` with the repo's configured kind/name and expects a bare version plus the artifact path.

Examples:

```bash
jwa-harden run -- ./scripts/release.sh 1.2.3 build/App.dmg
jwa-harden run -- ./scripts/release.sh 1.2.3 dist/tool.tar.gz
```

The script adds the `v` prefix where needed. Pass the bare version unless the script's own usage says otherwise.

## Common failures

- `$GITHUB_TOKEN not set`: run through `jwa-harden run --` from a repo that has `.env.template`.
- `goreleaser` reports a dirty tree: commit, stash, or intentionally discard unrelated local edits before release.
- `notarytool` or signing identity missing: run `jwa-harden doctor signing` and fix the reported prerequisite.
- Multi-platform tap entries should not be bumped with `jwa-tobrew bump`; release from the source repo's GoReleaser config instead.

## Operational learnings (CI + hardening)

- Prefer pinned tool versions in workflows over `@latest` (`govulncheck` in particular can raise its minimum Go version and break stable pipelines).
- Keep vulnerability scanning visible, but avoid blocking merges on standard-library advisories when the fix requires a Go upgrade you are not taking yet; treat CI vulnerability checks as advisory in that phase.
- When linting rules rely on git metadata, fetch tags in CI (`fetch-depth: 0` or explicit `git fetch --tags`) so version/changelog rules evaluate correctly.
- Avoid mutating runner git remotes in workflows unless absolutely required; adapt lint rules for CI context instead of rewriting `origin`.
