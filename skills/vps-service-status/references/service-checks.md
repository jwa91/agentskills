# Service Health Check Patterns

Replace `<vps-host>` with your SSH alias. All commands here are read-only.

The patterns below are recipes — adapt them to whatever services you run.
Each one combines "is the container up?" with a lightweight reachability
probe (an HTTP status code, `compose ps`, or a process check).

## Container present + HTTP healthcheck

For a service that exposes an HTTP health endpoint on a known internal port:

```bash
ssh <vps-host> "docker ps | grep <service> && curl -s -o /dev/null -w '%{http_code}' http://localhost:<port>/<health-path>"
```

Examples of common health paths: `/health`, `/healthz`, `/api/health`, `/-/healthy`.

## Multi-container compose stack

For a stack managed by `docker compose` (Supabase, monitoring stack, etc.):

```bash
ssh <vps-host> "cd /var/services/<service> && docker compose ps"
```

## Public URL probe

Verify the service is reachable from outside (DNS + TLS + reverse proxy):

```bash
ssh <vps-host> "curl -s -o /dev/null -w '%{http_code}' https://<subdomain>.<domain>"
```

Or run it locally without SSH if you want to test from your own machine:

```bash
curl -s -o /dev/null -w '%{http_code}' https://<subdomain>.<domain>
```

## Reverse proxy config (Caddy / Nginx)

List enabled sites to confirm the proxy knows about the service:

```bash
ssh <vps-host> "ls /etc/caddy/sites-enabled/"        # Caddy
ssh <vps-host> "ls /etc/nginx/sites-enabled/"        # Nginx
```

## Group of related containers

Check several containers in one shot using a regex:

```bash
ssh <vps-host> "docker ps | grep -E '(prometheus|grafana|cadvisor)'"
```
