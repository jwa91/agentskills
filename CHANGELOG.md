# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com); versions
follow [SemVer](https://semver.org).

## [Unreleased]

### Fixed

- Enforced notarization inside the GoReleaser build hook so releases cut via
  raw `goreleaser release --clean` are notarized (not only releases run via
  `make release`).

### Changed

- Added a generic `release` skill that detects repo-local `.goreleaser.yaml`
  or `scripts/release.sh` and routes releases through `jwa-harden`.
- Refreshed tap-related docs and skills to refer to `Casks/*.rb` and
  GoReleaser `homebrew_casks` for Go CLI distribution.

## [0.1.1] — 2026-05-13

### Changed

- **Migrate from `brews:` (Formula) to `homebrew_casks:` (Cask)** per
  [ADR 0008 in jwa91/homebrew-tap](https://github.com/jwa91/homebrew-tap/blob/main/docs/adr/0008-one-binary-per-repo-and-homebrew-casks.md).
  GoReleaser deprecated `brews:` in v2.10. End-user `brew install
  jwa91/tap/agentskills` is unchanged (modern brew auto-detects).
- **Codesign + notarize darwin binaries** with Developer ID Application.
  Required because macOS Tahoe Gatekeeper blocks unsigned binaries
  delivered through Casks. `scripts/codesign.sh` (invoked as goreleaser
  `builds.hooks.post`) and `scripts/notarize-darwin.sh` (invoked by the
  Makefile `release` target) submit each codesigned binary to
  `xcrun notarytool`. Archive sha256 is byte-identical pre/post.
- **CI release workflow** switched to `workflow_dispatch`-only — tag
  pushes no longer trigger automatic releases (CI cannot codesign
  without secrets). Canonical release path is `make release
  VERSION=X.Y.Z` locally.
- **`.env.template`** added (didn't exist before — releases were
  CI-only). Uses `HOMEBREW_TAP_GITHUB_TOKEN` for the Cask commit;
  `GITHUB_TOKEN` for the source-repo release is injected from
  `gh auth token` at release time. Adds `MACOS_SIGN_IDENTITY` for
  the codesign step.
- **Makefile `release` target** added (didn't exist — local release
  was not part of the previous flow). Same shape as the sibling
  `jwa-*` CLIs.

### Notes

- Skill content under `skills/` is unaffected by this change. The
  `agentskills bootstrap` mechanism for materializing skills into
  consuming repos works identically — the binary is what got signed.

## [0.1.0] — earlier

Initial release. See git history.

[Unreleased]: https://github.com/jwa91/agentskills/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/jwa91/agentskills/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/jwa91/agentskills/releases/tag/v0.1.0
