---
name: vps-service-status
description: Quick health checks for a Dockerized VPS. Use to verify services are running, check container status, view logs, or get a system overview (disk, memory, CPU). Read-only by design — anything that would change state is routed through the clipboard for the user to paste.
metadata:
  version: 0.1.0
---

# VPS Service Status

Quick health checks over SSH for a VPS that hosts Docker services.

## Safety invariant

**Direct `ssh` commands in this skill must be read-only.** Any command that changes
state (sudo, systemctl, docker compose up/down/restart, prune, etc.) goes through
the clipboard so the user pastes it manually. This keeps the skill safe to run
without per-command confirmation. Do not relax this rule when extending the skill.

## Configuration

This skill assumes:

- An SSH alias is configured in `~/.ssh/config` for the VPS (so `ssh <alias>`
  connects without further flags). Below, `<vps-host>` is a placeholder for that
  alias — replace with whatever you use (e.g. `hetzner`, `prod`, `myvps`).
- Services are managed with `docker compose` and live under a known root such as
  `/var/services/<service>/` or `/srv/<service>/`. Adjust paths to match your VPS.
- The clipboard helper is `pbcopy` (macOS). On Linux substitute `xclip -selection clipboard`
  or `wl-copy`.

If the user has not told you their SSH alias or service root, ask once before running.

## System Overview (direct, read-only)

```bash
ssh <vps-host> "echo '=== Containers ===' && docker ps --format 'table {{.Names}}\t{{.Status}}' && echo && echo '=== Disk ===' && df -h / && echo && echo '=== Memory ===' && free -h"
```

## Containers (direct, read-only)

```bash
ssh <vps-host> "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
ssh <vps-host> "cd /var/services/<service> && docker compose logs --tail 30"
```

## System Services (clipboard — needs sudo)

`sudo` over a non-interactive SSH command will fail (no TTY for the password
prompt), so these are copied to the clipboard for the user to paste after
SSH'ing in manually:

```bash
echo 'sudo systemctl status <unit> --no-pager' | pbcopy
echo 'sudo systemctl status caddy --no-pager' | pbcopy
echo 'sudo systemctl status webhook --no-pager' | pbcopy
```

## Recent Deployments (clipboard — needs sudo)

```bash
echo 'sudo journalctl -u <unit> --since "1 hour ago" | grep -E "(Starting|finished|ERROR)"' | pbcopy
```

## Detailed Checks

- Resource monitoring (disk, memory, CPU, network): [references/resources.md](references/resources.md)
- Per-service health endpoint patterns: [references/service-checks.md](references/service-checks.md)
