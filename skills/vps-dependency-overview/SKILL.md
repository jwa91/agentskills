---
name: vps-dependency-overview
description: Generate an offline-first dependency overview across services in a Docker-compose monorepo. Reports image tags & pinning quality, Dockerfile base images, runtime hints (Node/Python via .nvmrc, .python-version, package.json engines, pyproject.toml), and lockfile presence. Use when you want a single report of "what am I running and where are my update surfaces?" — no network calls, no pulls.
metadata:
  version: 0.2.0
---

# Dependency Overview (Docker-compose monorepo)

Inventory script that walks a `services/` directory of Docker-compose stacks and produces a Markdown or JSON report of:

- **Compose images** — `image:` references with tag/digest, classified by pinning quality (`floating`, `implicit-latest`, `major`, `minor`, `semver`, `digest`, `custom`)
- **Build services** — `FROM` lines from Dockerfiles, useful for spotting outdated base images
- **Runtime hints** — Node/Python versions inferred from `.nvmrc`, `.node-version`, `.python-version`, `package.json` engines, `pyproject.toml`
- **Dependency manager signals** — which lockfiles exist (`pnpm-lock.yaml`, `package-lock.json`, `poetry.lock`, `uv.lock`, …)
- **Per-service update-check skills** — `<service>/.agents/skills/*-update-check/` if you've put deeper version-checking skills next to each service

It does **not** hit the network. It answers "what am I using?", not "what's the latest?".

## Quick Start

From the repo root, with `docker compose` (v2) available locally:

```bash
python3 .agents/skills/vps-dependency-overview/scripts/vps_dependency_overview.py \
  --format markdown \
  --output /tmp/dependency-overview.md
```

Print to stdout instead:

```bash
python3 .agents/skills/vps-dependency-overview/scripts/vps_dependency_overview.py --format markdown
```

Focus on specific service folders:

```bash
python3 .agents/skills/vps-dependency-overview/scripts/vps_dependency_overview.py --only n8n --only postgres
```

JSON output for downstream tooling:

```bash
python3 .agents/skills/vps-dependency-overview/scripts/vps_dependency_overview.py --format json
```

## Flags

| Flag             | Default    | Description                                            |
| ---------------- | ---------- | ------------------------------------------------------ |
| `--root`         | `.`        | Workspace root                                         |
| `--services-dir` | `services` | Subdirectory containing per-service folders            |
| `--format`       | `markdown` | `markdown` or `json`                                   |
| `--output`       | stdout     | Write to a file instead of stdout                      |
| `--only NAME`    | all        | Restrict to specific service folder names (repeatable) |

## Expected layout

```
<root>/
  <services-dir>/             # default: services/
    <service-a>/
      docker-compose.yml      # required for the service to be inventoried
      Dockerfile              # optional, parsed if present
      .nvmrc / .python-version / package.json / pyproject.toml   # optional, parsed for runtime hints
      .agents/skills/<svc>-update-check/SKILL.md                 # optional, surfaced in the report
    <service-b>/
      ...
```

A service folder without `docker-compose.yml` is skipped silently.

## Requirements

- Python 3.11+ (uses `tomllib`)
- `docker` with Compose v2 (the script invokes `docker compose -f … config --format json` to resolve compose files; no images are pulled or built)

## Optional: live container versions on a remote host

The script reports **desired** versions (what the compose files say). To compare against **actually running** versions on a remote VPS, run separately:

```bash
ssh <vps-host> "docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'"
```

Replace `<vps-host>` with your SSH alias from `~/.ssh/config`.

## How to read the report

| Pinning class     | What it means                                | Reproducibility                            |
| ----------------- | -------------------------------------------- | ------------------------------------------ |
| `digest`          | `image@sha256:…`                             | Best — content-addressed                   |
| `semver`          | `1.2.3`, `v1.2.3`, `1.2.3-alpine`            | Good — explicit version                    |
| `minor`           | `1.2`, `1.2-alpine`                          | Major+minor pinned, patches float          |
| `major`           | `22`, `3-slim`                               | Major pinned, minor+patch float on rebuild |
| `floating`        | `latest`, `main`, `master`, `edge`, `stable` | Bad — non-reproducible                     |
| `implicit-latest` | no tag at all                                | Bad — equivalent to `:latest`              |
| `custom`          | anything else                                | Worth a manual look                        |

Runtime fields:

- `node_container` / `python_container` — inferred from Dockerfile `FROM` lines (the runtime your container actually runs)
- `node_repo` / `python_repo` — inferred from `.nvmrc`/`.python-version` (what dev tooling expects)
- `node_engine` / `python_requires` — explicit constraints from `package.json`/`pyproject.toml`

A common red flag: `node_container=18` while `node_repo=22` means your dev environment and your container are on different majors.
