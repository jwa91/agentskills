# Resource Monitoring

Replace `<vps-host>` with your SSH alias. All commands here are read-only.
Anything that changes state (`prune`, port scans needing root) is routed
through the clipboard.

## Disk

```bash
ssh <vps-host> "df -h"
ssh <vps-host> "docker system df"
ssh <vps-host> "du -sh /var/services/* 2>/dev/null | sort -rh | head -10"
```

## Memory

```bash
ssh <vps-host> "free -h"
ssh <vps-host> "ps aux --sort=-%mem | head -10"
```

## CPU

```bash
ssh <vps-host> "uptime"
ssh <vps-host> "ps aux --sort=-%cpu | head -10"
```

## Network (clipboard — needs sudo)

```bash
echo 'sudo ss -tlnp' | pbcopy
echo 'sudo ss -tlnp | grep :<port>' | pbcopy
```

## Docker Cleanup (clipboard — state-changing)

These delete containers, images, and (with `--volumes`) data. Always go
through the clipboard so the user can review and paste manually:

```bash
echo 'docker system prune -f' | pbcopy
echo 'docker system prune -af --volumes' | pbcopy   # destructive, removes volumes
```
