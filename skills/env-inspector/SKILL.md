---
name: env-inspector
description: Safely inspect .env files by showing key names and clearly non-sensitive values while redacting anything that looks like a secret. Best-effort heuristic redaction (keyword block + token-pattern blocklist + Shannon-entropy check + value allowlist) — not a cryptographic guarantee. Use when you need to understand a project's environment configuration without exposing credentials.
metadata:
  version: 0.2.0
hooks:
  PreToolUse:
    - matcher: Bash
      hooks:
        - type: command
          command: ${CLAUDE_PROJECT_DIR}/.agents/skills/env-inspector/hooks/path-gate.sh
---

# ENV Inspector

Reads `.env` files and emits a redacted view: keys are always shown, values are shown only when they look unambiguously safe. Anything ambiguous is replaced with `<redacted>`.

## Usage

```bash
bash .agents/skills/env-inspector/scripts/env-safe-read.sh /path/to/.env
```

Inspect every `.env*` in a project (excluding examples):

```bash
for f in $(find . -maxdepth 3 -name '.env*' -not -name '.env.example' -not -path '*/node_modules/*'); do
  echo "--- $f ---"
  bash .agents/skills/env-inspector/scripts/env-safe-read.sh "$f"
  echo ""
done
```

## How redaction works

Four layers, all default-deny. A value is shown only if it survives all of them:

1. **Sensitive-key block.** Keys matching `KEY|SECRET|TOKEN|PASSWORD|PASS|CREDENTIAL|AUTH|PRIVATE|SIGNING|HASH|SALT|ENCRYPTION|JWT|BEARER|COOKIE|CSRF|SESSION|DSN|WEBHOOK_URL` are redacted regardless of value.
2. **Token-pattern blocklist.** Values matching known shapes (`sk-…`, `pk_live_…`, `ghp_…`, `github_pat_…`, `eyJ…` JWT, `AKIA…`, `xox[abprs]-…`, `AIza…`, `glpat-…`, `npm_…`, `dckr_pat_…`) are redacted.
3. **Shannon entropy.** Values ≥16 chars with entropy ≥3.5 bits/char are redacted (catches random tokens that don't match a known prefix).
4. **Positive allowlist.** What survives is shown only if it matches a known-safe shape: booleans, numbers, log levels, localhost/loopback, short non-random strings (≤20 chars), or HTTP(S) URLs without embedded `@` credentials and without long random query strings.

## What this skill is and isn't

- **Is:** a heuristic that makes leaks much less likely when summarizing env config.
- **Isn't:** a cryptographic guarantee. A short, human-chosen password under an innocent key (e.g. `MY_PIN=hunter12`) can still slip through.
- For high-stakes contexts (production secrets, audit logs), inspect manually instead.

## Path-gate hook

The skill ships with a `PreToolUse` hook (`hooks/path-gate.sh`) that:

- Allows `env-safe-read.sh` to run only against paths inside `$CLAUDE_PROJECT_DIR`.
- Rejects any target whose filename doesn't match a `.env` pattern.
- Rejects paths containing `..` traversal.

The hook is **a guardrail, not the primary defense** — the redaction in the script is what protects you. The hook just ensures the script can't be aimed at, say, `/etc/postgresql/.env` by an over-eager agent.

If your harness doesn't honor skill-level `hooks` frontmatter, copy the matcher block into your project `.claude/settings.json` or run the script manually.

## Compatibility

- Requires `bash` and `awk` (entropy calc). No Python or jq dependency.
- The hook uses `sed` for JSON parsing to avoid a `jq` dep — fragile but works for the standard Claude Code tool-call shape.
