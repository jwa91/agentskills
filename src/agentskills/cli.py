#!/usr/bin/env python3
"""CLI entrypoint for agentskills."""

from __future__ import annotations

import sys

COMMANDS = {
    "bootstrap": "Install skills into a project",
    "link": "Create harness symlinks for a project",
    "package": "Package a skill into a .skill archive",
    "release": "Validate and package a skill",
}


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("usage: agentskills <command> [args]\n")
        print("commands:")
        for name, desc in COMMANDS.items():
            print(f"  {name:12s} {desc}")
        return 0

    command = sys.argv[1]
    sys.argv = [f"agentskills {command}", *sys.argv[2:]]

    if command == "bootstrap":
        from agentskills.bootstrap import main as cmd
    elif command == "link":
        from agentskills.link import main as cmd
    elif command == "package":
        from agentskills.package import main as cmd
    elif command == "release":
        from agentskills.release import main as cmd
    else:
        print(f"error: unknown command '{command}'")
        print(f"available: {', '.join(COMMANDS)}")
        return 1

    return cmd()


if __name__ == "__main__":
    raise SystemExit(main())
