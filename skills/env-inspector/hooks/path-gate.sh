#!/bin/bash
# PreToolUse path gate for env-inspector.
#
# Prevents env-safe-read.sh from being pointed at .env files outside the
# project workspace, and refuses non-.env-pattern targets. This is a
# guardrail layer; the redaction logic itself lives in env-safe-read.sh.
#
# Receives Claude Code tool-call JSON on stdin. Allow = exit 0;
# block = exit 2 with a message on stderr (shown to the model).

set -euo pipefail

INPUT=$(cat)

# We only inspect Bash tool calls. Non-Bash calls aren't ours to gate.
TOOL=$(printf '%s' "$INPUT" | sed -n 's/.*"tool_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n1)
[ "$TOOL" = "Bash" ] || exit 0

# Pull tool_input.command using a simple regex (avoids a jq dep).
# This won't handle commands containing escaped quotes — fine for our case,
# where the command is just a script path + file path.
CMD=$(printf '%s' "$INPUT" | sed -n 's/.*"command"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n1)

# Only act on commands that invoke env-safe-read.sh
echo "$CMD" | grep -qE 'env-safe-read\.sh' || exit 0

# Best-effort path extraction: grab the first .env-shaped token in the command.
TARGET=$(printf '%s' "$CMD" | tr -s ' \t' '\n' | grep -E '\.env(\.[A-Za-z0-9_-]+)?$' | head -n1 || true)
TARGET="${TARGET%\"}" ; TARGET="${TARGET#\"}"
TARGET="${TARGET%\'}" ; TARGET="${TARGET#\'}"

if [ -z "$TARGET" ]; then
  echo "env-inspector path-gate: no .env target found in command: $CMD" >&2
  exit 2
fi

# Resolve absolute path without requiring the file to exist (it should, but
# we want the error message to come from env-safe-read.sh, not from us).
case "$TARGET" in
  /*) ABS_TARGET="$TARGET" ;;
  *)  ABS_TARGET="$(pwd)/$TARGET" ;;
esac

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
case "$PROJECT_DIR" in
  /*) ABS_PROJECT="$PROJECT_DIR" ;;
  *)  ABS_PROJECT="$(pwd)/$PROJECT_DIR" ;;
esac

# Containment check via canonical-ish prefix match. Reject paths that escape
# the project root, even via .. traversal (they won't normalize cleanly).
case "$ABS_TARGET" in
  "$ABS_PROJECT"/*|"$ABS_PROJECT") ;;
  *)
    echo "env-inspector path-gate: refusing to read $ABS_TARGET — outside project root $ABS_PROJECT" >&2
    exit 2
    ;;
esac
case "$ABS_TARGET" in
  *..*)
    echo "env-inspector path-gate: refusing to read $ABS_TARGET — path traversal not allowed" >&2
    exit 2
    ;;
esac

# Filename must match a .env pattern.
BASENAME=$(basename "$ABS_TARGET")
case "$BASENAME" in
  .env|.env.*|*.env) ;;
  *)
    echo "env-inspector path-gate: refusing to read $ABS_TARGET — not a .env-pattern filename" >&2
    exit 2
    ;;
esac

exit 0
