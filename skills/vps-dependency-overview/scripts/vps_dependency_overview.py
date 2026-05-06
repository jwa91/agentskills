#!/usr/bin/env python3
from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable


@dataclasses.dataclass(frozen=True)
class ImageRef:
    raw: str
    name: str
    tag: str | None
    digest: str | None

    @property
    def has_explicit_tag(self) -> bool:
        return self.tag is not None and self.tag != ""

    @property
    def implied_latest(self) -> bool:
        return not self.has_explicit_tag and self.digest is None

    @property
    def pinning(self) -> str:
        if self.digest:
            return "digest"
        if not self.has_explicit_tag:
            return "implicit-latest"
        if self.tag in {"latest", "main", "master", "edge", "stable"}:
            return "floating"
        if _looks_like_semver(self.tag):
            return "semver"
        if _looks_like_major_only(self.tag):
            return "major"
        if _looks_like_major_minor(self.tag):
            return "minor"
        return "custom"


@dataclasses.dataclass
class BuildRef:
    service: str
    context: str | None
    dockerfile: str | None
    dockerfile_path: str | None
    base_images: list[ImageRef]


@dataclasses.dataclass
class ServiceInventory:
    name: str
    path: str
    compose_path: str
    compose_services: list[str]
    images: dict[str, ImageRef]
    builds: list[BuildRef]
    runtime_hints: dict[str, str]
    dependency_hints: dict[str, Any]
    update_check_skills: list[str]
    warnings: list[str]
    errors: list[str]


def _looks_like_semver(tag: str) -> bool:
    # Accept vX.Y.Z, X.Y.Z, X.Y.Z-suffix, X.Y.Z+meta
    return bool(re.match(r"^v?\d+\.\d+\.\d+([\-+].+)?$", tag))


def _looks_like_major_only(tag: str) -> bool:
    # e.g. "22", "16-alpine", "3-slim"
    return bool(re.match(r"^v?\d+([\-].+)?$", tag))


def _looks_like_major_minor(tag: str) -> bool:
    # e.g. "3.12", "3.12-slim", "22.11-alpine"
    return bool(re.match(r"^v?\d+\.\d+([\-].+)?$", tag))


def _parse_image_ref(raw: str) -> ImageRef:
    digest = None
    name_and_tag = raw
    if "@" in raw:
        name_and_tag, digest = raw.split("@", 1)

    # Split tag from name using "last colon after last slash" heuristic.
    last_slash = name_and_tag.rfind("/")
    last_colon = name_and_tag.rfind(":")
    if last_colon > last_slash:
        name = name_and_tag[:last_colon]
        tag = name_and_tag[last_colon + 1 :]
    else:
        name = name_and_tag
        tag = None

    return ImageRef(raw=raw, name=name, tag=tag, digest=digest)


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def _compose_config_json(compose_path: Path) -> tuple[dict[str, Any] | None, str | None]:
    cmd = [
        "docker",
        "compose",
        "-f",
        str(compose_path),
        "config",
        "--format",
        "json",
        "--no-interpolate",
        "--no-env-resolution",
        "--no-path-resolution",
    ]
    result = _run(cmd, cwd=compose_path.parent)
    if result.returncode != 0:
        err = (result.stderr or result.stdout or "").strip()
        return None, err or "docker compose config failed"
    try:
        return json.loads(result.stdout), None
    except json.JSONDecodeError as e:
        return None, f"Failed to parse compose JSON: {e}"


def _extract_base_images_from_dockerfile(dockerfile_path: Path) -> list[ImageRef]:
    if not dockerfile_path.exists():
        return []
    images: list[ImageRef] = []
    for raw_line in dockerfile_path.read_text(errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if not line.upper().startswith("FROM "):
            continue
        remainder = line[5:].strip()
        # Strip flags like: FROM --platform=linux/amd64 node:22-alpine AS build
        while remainder.startswith("--"):
            parts = remainder.split(None, 1)
            if len(parts) == 1:
                remainder = ""
                break
            remainder = parts[1].lstrip()
        if not remainder:
            continue
        image_token = remainder.split(None, 1)[0]
        images.append(_parse_image_ref(image_token))
    return images


def _dedupe_images(images: Iterable[ImageRef]) -> list[ImageRef]:
    seen: set[str] = set()
    out: list[ImageRef] = []
    for img in images:
        if img.raw in seen:
            continue
        seen.add(img.raw)
        out.append(img)
    return out


def _read_first_line(path: Path) -> str | None:
    if not path.exists():
        return None
    for line in path.read_text(errors="replace").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            return line
    return None


def _try_load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _try_load_toml(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        import tomllib  # py3.11+

        return tomllib.loads(path.read_text())
    except Exception:
        return None


def _detect_runtime_hints(service_dir: Path, dockerfile_base_images: Iterable[ImageRef]) -> dict[str, str]:
    """
    Prefer explicit "container runtime" signals from Dockerfiles, while retaining repo constraints.

    Keys used:
      - node_container, python_container: inferred from Dockerfile base images
      - node_repo, python_repo: inferred from repo pin files (.nvmrc/.python-version)
      - node_engine, python_requires: inferred from package.json engines / pyproject.toml
      - packageManager: e.g. pnpm@9.0.0, bun@1.2.0
    """
    hints: dict[str, str] = {}

    nvmrc = _read_first_line(service_dir / ".nvmrc")
    node_repo = nvmrc or _read_first_line(service_dir / ".node-version")
    if node_repo:
        hints["node_repo"] = node_repo.lstrip("v")

    python_repo = _read_first_line(service_dir / ".python-version")
    if python_repo:
        hints["python_repo"] = python_repo

    package_json = _try_load_json(service_dir / "package.json")
    if package_json:
        engines = package_json.get("engines") if isinstance(package_json.get("engines"), dict) else None
        if engines and isinstance(engines.get("node"), str):
            hints["node_engine"] = engines["node"]
        pm = package_json.get("packageManager")
        if isinstance(pm, str):
            hints["packageManager"] = pm

    pyproject = _try_load_toml(service_dir / "pyproject.toml")
    if pyproject:
        project = pyproject.get("project") if isinstance(pyproject.get("project"), dict) else None
        if project and isinstance(project.get("requires-python"), str):
            hints["python_requires"] = project["requires-python"]

        tool = pyproject.get("tool") if isinstance(pyproject.get("tool"), dict) else None
        poetry = tool.get("poetry") if isinstance(tool, dict) else None
        if isinstance(poetry, dict):
            deps = poetry.get("dependencies") if isinstance(poetry.get("dependencies"), dict) else None
            if deps and isinstance(deps.get("python"), str):
                hints.setdefault("python_requires", deps["python"])

    # Dockerfile base images (container runtime)
    for image in dockerfile_base_images:
        base = image.name.split("/")[-1]
        if base == "node" and image.tag and "node_container" not in hints:
            hints["node_container"] = image.tag.split("-", 1)[0].lstrip("v")
        if base == "python" and image.tag and "python_container" not in hints:
            hints["python_container"] = image.tag.split("-", 1)[0].lstrip("v")

    return hints


def _detect_dependency_hints(service_dir: Path) -> dict[str, Any]:
    hints: dict[str, Any] = {}

    lockfiles = []
    for name in [
        "pnpm-lock.yaml",
        "package-lock.json",
        "yarn.lock",
        "bun.lockb",
        "poetry.lock",
        "uv.lock",
        "Pipfile.lock",
        "requirements.txt",
        "requirements-dev.txt",
    ]:
        if (service_dir / name).exists():
            lockfiles.append(name)
    if lockfiles:
        hints["lockfiles"] = lockfiles

    if (service_dir / "package.json").exists():
        hints["nodeProject"] = True
    if (service_dir / "pyproject.toml").exists() or (service_dir / "requirements.txt").exists():
        hints["pythonProject"] = True

    return hints


def _discover_update_check_skills(service_dir: Path, *, root: Path) -> list[str]:
    skills_dir = service_dir / ".agents" / "skills"
    if not skills_dir.exists():
        return []
    matches: list[str] = []
    for child in sorted(skills_dir.iterdir()):
        if not child.is_dir():
            continue
        name = child.name.lower()
        if "update-check" in name or name.endswith("-update") or "upgrade" in name:
            if (child / "SKILL.md").exists():
                matches.append(_relpath(child, root))
    return matches


def _relpath(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except Exception:
        return str(path.resolve())


def _inventory_service(service_dir: Path, *, root: Path) -> ServiceInventory | None:
    compose_path = service_dir / "docker-compose.yml"
    if not compose_path.exists():
        return None

    warnings: list[str] = []
    errors: list[str] = []

    compose, compose_error = _compose_config_json(compose_path)
    if compose_error:
        errors.append(compose_error)
        compose = {"services": {}}

    services_obj = compose.get("services") if isinstance(compose, dict) else None
    services: dict[str, Any] = services_obj if isinstance(services_obj, dict) else {}

    images: dict[str, ImageRef] = {}
    builds: list[BuildRef] = []
    dockerfile_bases: list[ImageRef] = []

    for service_name, cfg in services.items():
        if not isinstance(cfg, dict):
            continue
        image_str = cfg.get("image")
        if isinstance(image_str, str) and image_str.strip():
            images[service_name] = _parse_image_ref(image_str.strip())
            if images[service_name].pinning in {"implicit-latest", "floating"}:
                warnings.append(f"{service_name}: image tag is floating ({images[service_name].raw})")

        build_cfg = cfg.get("build")
        if build_cfg is None:
            continue

        context: str | None = None
        dockerfile: str | None = None
        dockerfile_path: str | None = None
        if isinstance(build_cfg, str):
            context = build_cfg
        elif isinstance(build_cfg, dict):
            context_val = build_cfg.get("context")
            dockerfile_val = build_cfg.get("dockerfile")
            context = context_val if isinstance(context_val, str) else None
            dockerfile = dockerfile_val if isinstance(dockerfile_val, str) else None

        context_path = (service_dir / (context or ".")).resolve()
        dockerfile_rel = dockerfile or "Dockerfile"
        df_path = (context_path / dockerfile_rel).resolve()
        dockerfile_path = _relpath(df_path, root)
        base_images = _extract_base_images_from_dockerfile(df_path)
        dockerfile_bases.extend(_dedupe_images(base_images))
        if not base_images:
            warnings.append(f"{service_name}: build Dockerfile has no parsable FROM lines ({df_path})")
        builds.append(
            BuildRef(
                service=service_name,
                context=context,
                dockerfile=dockerfile_rel,
                dockerfile_path=dockerfile_path,
                base_images=_dedupe_images(base_images),
            )
        )

    runtime_hints = _detect_runtime_hints(service_dir, dockerfile_bases)
    dependency_hints = _detect_dependency_hints(service_dir)
    update_check_skills = _discover_update_check_skills(service_dir, root=root)

    return ServiceInventory(
        name=service_dir.name,
        path=_relpath(service_dir, root),
        compose_path=_relpath(compose_path, root),
        compose_services=sorted(services.keys()),
        images=images,
        builds=builds,
        runtime_hints=runtime_hints,
        dependency_hints=dependency_hints,
        update_check_skills=update_check_skills,
        warnings=warnings,
        errors=errors,
    )


def _md_escape(text: str) -> str:
    return text.replace("|", "\\|")


def _render_markdown(inventories: list[ServiceInventory], generated_at: str) -> str:
    lines: list[str] = []
    lines.append("# Service Dependency Overview")
    lines.append("")
    lines.append(f"Generated: `{generated_at}`")
    lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.append(
        "| Service | Compose svcs | Images | Builds | Runtimes | Locks | Update-check skill | Warnings | Errors |"
    )
    lines.append("|---|---:|---:|---:|---|---|---|---:|---:|")

    for inv in inventories:
        runtime_bits = []
        if "node_container" in inv.runtime_hints:
            runtime_bits.append(f"node={inv.runtime_hints['node_container']}")
        if "python_container" in inv.runtime_hints:
            runtime_bits.append(f"python={inv.runtime_hints['python_container']}")
        runtimes = ", ".join(runtime_bits)
        locks = ", ".join(inv.dependency_hints.get("lockfiles", [])) if isinstance(inv.dependency_hints.get("lockfiles"), list) else ""
        has_update_skill = "yes" if inv.update_check_skills else ""
        lines.append(
            "| "
            + " | ".join(
                [
                    _md_escape(inv.name),
                    str(len(inv.compose_services)),
                    str(len(inv.images)),
                    str(len(inv.builds)),
                    _md_escape(runtimes),
                    _md_escape(locks),
                    has_update_skill,
                    str(len(inv.warnings)),
                    str(len(inv.errors)),
                ]
            )
            + " |"
        )

    for inv in inventories:
        lines.append("")
        lines.append(f"## {inv.name}")
        lines.append("")
        lines.append(f"- Path: `{inv.path}`")
        lines.append(f"- Compose: `{inv.compose_path}`")

        if inv.compose_services:
            lines.append(f"- Compose services: {', '.join(f'`{s}`' for s in inv.compose_services)}")
        if inv.runtime_hints:
            lines.append(
                "- Runtime hints: "
                + ", ".join(f"`{k}={v}`" for k, v in sorted(inv.runtime_hints.items()))
            )
        if inv.dependency_hints.get("lockfiles"):
            lines.append(
                "- Lockfiles: " + ", ".join(f"`{lf}`" for lf in inv.dependency_hints["lockfiles"])
            )

        if inv.images:
            lines.append("- Images:")
            for svc, img in sorted(inv.images.items()):
                tag = img.tag if img.tag is not None else "(no tag)"
                digest = f"@{img.digest}" if img.digest else ""
                lines.append(
                    f"  - `{svc}`: `{img.name}` `{tag}`{digest} ({img.pinning})"
                )

        if inv.builds:
            lines.append("- Builds:")
            for b in inv.builds:
                if b.base_images:
                    bases = ", ".join(f"`{i.raw}`" for i in b.base_images)
                else:
                    bases = "(none found)"
                lines.append(
                    f"  - `{b.service}`: Dockerfile `{b.dockerfile_path}` (bases: {bases})"
                )

        if inv.update_check_skills:
            lines.append("- Per-service update-check skills:")
            for p in inv.update_check_skills:
                lines.append(f"  - `{p}`")

        if inv.warnings:
            lines.append("- Warnings:")
            for w in inv.warnings:
                lines.append(f"  - {_md_escape(w)}")
        if inv.errors:
            lines.append("- Errors:")
            for e in inv.errors:
                lines.append(f"  - {_md_escape(e)}")

    lines.append("")
    return "\n".join(lines)


def _render_json(inventories: list[ServiceInventory], generated_at: str) -> str:
    def _to_dict(inv: ServiceInventory) -> dict[str, Any]:
        return {
            "name": inv.name,
            "path": inv.path,
            "compose_path": inv.compose_path,
            "compose_services": inv.compose_services,
            "images": {k: dataclasses.asdict(v) for k, v in inv.images.items()},
            "builds": [
                {
                    "service": b.service,
                    "context": b.context,
                    "dockerfile": b.dockerfile,
                    "dockerfile_path": b.dockerfile_path,
                    "base_images": [dataclasses.asdict(i) for i in b.base_images],
                }
                for b in inv.builds
            ],
            "runtime_hints": inv.runtime_hints,
            "dependency_hints": inv.dependency_hints,
            "update_check_skills": inv.update_check_skills,
            "warnings": inv.warnings,
            "errors": inv.errors,
        }

    payload = {
        "generated_at": generated_at,
        "cwd": os.getcwd(),
        "services": [_to_dict(i) for i in inventories],
    }
    return json.dumps(payload, indent=2)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate a dependency overview across all services in a Docker-compose monorepo.")
    p.add_argument("--root", default=".", help="Workspace root (default: .)")
    p.add_argument("--services-dir", default="services", help="Services directory (default: services)")
    p.add_argument("--format", default="markdown", choices=["markdown", "json"])
    p.add_argument("--output", help="Write output to a file instead of stdout")
    p.add_argument(
        "--only",
        action="append",
        default=[],
        help="Only include a specific service folder name (repeatable)",
    )
    return p.parse_args(argv)


def main(argv: list[str]) -> int:
    args = _parse_args(argv)

    root = Path(args.root).resolve()
    services_dir = (root / args.services_dir).resolve()
    if not services_dir.exists():
        print(f"Services dir not found: {services_dir}", file=sys.stderr)
        return 2

    allow = set(args.only or [])

    inventories: list[ServiceInventory] = []
    for service_dir in sorted(p for p in services_dir.iterdir() if p.is_dir()):
        if allow and service_dir.name not in allow:
            continue
        inv = _inventory_service(service_dir, root=root)
        if inv is not None:
            inventories.append(inv)

    generated_at = dt.datetime.now(tz=dt.timezone.utc).isoformat()
    if args.format == "json":
        output = _render_json(inventories, generated_at)
    else:
        output = _render_markdown(inventories, generated_at)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
    else:
        print(output)

    # Non-zero exit when there were hard errors parsing compose files.
    any_errors = any(i.errors for i in inventories)
    return 1 if any_errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
