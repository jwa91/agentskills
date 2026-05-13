---
name: jwa-harden
description: Use the `jwa-harden` CLI for secret-safe command execution, env-template discovery, and signing/notarization preflight checks. Trigger when a command needs secrets, when `.env.template` or 1Password references are involved, or before signed release flows.
---

# jwa-harden — Secret-Safe Command Runner

`jwa-harden` wraps commands with 1Password CLI environment resolution. It walks
up from the current directory to find the nearest `.env.template`, then execs:

```bash
op run --env-file=<found> -- <command>
```

Use it whenever a command needs secrets from `op://` references. Do not load or
print real `.env` files.

## Command Surface

```bash
jwa-harden run -- <command> [args...]   # resolve env and run command
jwa-harden doctor                       # check op, signin, and .env.template discovery
jwa-harden doctor signing               # check codesign/notary prerequisites
jwa-harden version                      # print build info
```

## Release Usage

For GoReleaser-owned projects:

```bash
jwa-harden run -- goreleaser release --clean
```

For script-owned cask/formula projects:

```bash
jwa-harden run -- ./scripts/release.sh <version> <path/to/artifact>
```

Run `jwa-harden doctor` first. For signed macOS artifacts, also run
`jwa-harden doctor signing`.

## Boundary

- `jwa-harden` owns env-template discovery and process execution through `op`.
- It does not read, validate, or store secrets itself.
- Publishing mechanics belong to `jwa-tobrew` or the target repo's release
  backend.
- Real `.env` files must stay untracked; `.env.template` contains only
  `op://` references.
