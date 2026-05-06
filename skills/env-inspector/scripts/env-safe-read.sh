#!/bin/bash
# Reads .env files and emits a redacted view: shows key names always, shows
# values only when they look unambiguously non-sensitive. Default-deny.
#
# Layered checks (any one of them triggers redaction):
#   1. Sensitive-key keyword block (KEY, SECRET, TOKEN, ...)
#   2. Known token-pattern blocklist (sk-, ghp_, eyJ JWT, AKIA, ...)
#   3. Shannon entropy threshold for values >= 16 chars
#   4. Value-allowlist (booleans, numbers, log levels, localhost, short
#      non-random strings, http(s) URLs without embedded creds)
#
# This is best-effort, not cryptographically safe. A 19-char human-chosen
# password under an innocent key may still pass. Treat output as "much safer
# than the raw file", not "guaranteed clean".

set -euo pipefail

FILE="${1:-.env}"

if [ ! -f "$FILE" ]; then
  echo "File not found: $FILE" >&2
  exit 1
fi

# --- Layer 1: sensitive key names ----------------------------------------

is_sensitive_key() {
  local key="$1"
  echo "$key" | grep -qiE '(KEY|SECRET|TOKEN|PASSWORD|PASS|CREDENTIAL|AUTH|API_KEY|PRIVATE|SIGNING|HASH|SALT|ENCRYPTION|JWT|BEARER|COOKIE|CSRF|SESSION|DSN|WEBHOOK_URL)'
}

# --- Layer 2: known token-shape blocklist --------------------------------

is_known_token_pattern() {
  local val="$1"
  # OpenAI / Stripe / Anthropic-style
  echo "$val" | grep -qE '^sk-[A-Za-z0-9_-]{12,}'        && return 0
  echo "$val" | grep -qE '^pk_(live|test)_[A-Za-z0-9]{16,}' && return 0
  # GitHub
  echo "$val" | grep -qE '^gh[ousr]_[A-Za-z0-9]{30,}'    && return 0
  echo "$val" | grep -qE '^github_pat_[A-Za-z0-9_]{40,}' && return 0
  # JWT (header.payload.sig)
  echo "$val" | grep -qE '^eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.' && return 0
  # AWS
  echo "$val" | grep -qE '^A(KIA|SIA|ROA|IDA|GPA|NPA|PKA|3T)[A-Z0-9]{16}$' && return 0
  # Slack
  echo "$val" | grep -qE '^xox[abprs]-'                  && return 0
  # Google API
  echo "$val" | grep -qE '^AIza[A-Za-z0-9_-]{35}$'       && return 0
  # GitLab PAT
  echo "$val" | grep -qE '^glpat-[A-Za-z0-9_-]{20}'      && return 0
  # npm
  echo "$val" | grep -qE '^npm_[A-Za-z0-9]{36}$'         && return 0
  # Docker Hub
  echo "$val" | grep -qE '^dckr_pat_[A-Za-z0-9_-]{20,}'  && return 0
  # Supabase / PostgREST anon/service keys (long JWT-like, often start with eyJ — covered above)
  return 1
}

# --- Layer 3: Shannon entropy (via awk, no python dep) -------------------

shannon_entropy() {
  # Prints entropy in bits/char as a float. Uses awk for portability.
  local s="$1"
  printf '%s' "$s" | awk '
    {
      n = length($0)
      for (i = 1; i <= n; i++) count[substr($0, i, 1)]++
      total += n
    }
    END {
      if (total == 0) { printf "0"; exit }
      H = 0
      for (c in count) {
        p = count[c] / total
        H -= p * log(p) / log(2)
      }
      printf "%.4f", H
    }
  '
}

# Threshold: 3.5 bits/char over 16+ chars usually means "looks random".
# Plain English passwords are typically 2.5–3.0 bits/char.
is_high_entropy() {
  local val="$1"
  [ ${#val} -lt 16 ] && return 1
  local h
  h=$(shannon_entropy "$val")
  awk -v h="$h" 'BEGIN { exit !(h+0 >= 3.5) }'
}

# --- Layer 4: positive allowlist for clearly safe values -----------------

is_safe_value() {
  local val="$1"
  # Empty value
  [ -z "$val" ] && return 0
  # Boolean
  echo "$val" | grep -qiE '^(true|false|yes|no|on|off|enabled|disabled)$' && return 0
  # Number (int or port)
  echo "$val" | grep -qE '^[0-9]+$' && return 0
  # Log level / env mode
  echo "$val" | grep -qiE '^(debug|info|warn|warning|error|development|production|staging|test|verbose|trace)$' && return 0
  # Localhost / loopback
  echo "$val" | grep -qiE '^(localhost|127\.0\.0\.1|0\.0\.0\.0|::1)$' && return 0

  # HTTP(S) URLs — checked BEFORE entropy because URLs have moderate entropy
  # by nature. Reject URLs that embed creds (@) or carry long random tokens.
  if echo "$val" | grep -qE '^https?://'; then
    echo "$val" | grep -qE '@' && return 1
    echo "$val" | grep -qE '[A-Za-z0-9_-]{32,}' && return 1
    return 0
  fi

  # Known token shapes — always redact
  is_known_token_pattern "$val" && return 1
  # High-entropy values — always redact
  is_high_entropy "$val" && return 1
  # Short strings (<=20 chars) that don't look like base64/hex tokens
  if [ ${#val} -le 20 ]; then
    echo "$val" | grep -qE '^[A-Za-z0-9+/=_-]{12,}$' && return 1
    return 0
  fi
  return 1
}

# --- Main loop -----------------------------------------------------------

echo "# ENV inspection: $FILE"
echo "# Keys: ALL shown | Values: safe=shown, sensitive=<redacted>"
echo "# Heuristic redaction: best-effort, not a guarantee."
echo ""

while IFS= read -r line || [ -n "$line" ]; do
  if [[ "$line" =~ ^[[:space:]]*# ]] || [[ -z "${line// }" ]]; then
    echo "$line"
    continue
  fi
  [[ "$line" != *"="* ]] && continue

  key="${line%%=*}"
  val="${line#*=}"
  val="${val#\"}" ; val="${val%\"}"
  val="${val#\'}" ; val="${val%\'}"

  if is_sensitive_key "$key"; then
    echo "${key}=<redacted>"
  elif is_safe_value "$val"; then
    echo "${key}=${val}"
  else
    echo "${key}=<redacted>"
  fi
done < "$FILE"
