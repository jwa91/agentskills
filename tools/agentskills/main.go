// Command agentskills installs and manages agent skills inside a project.
//
// The Go binary is a transport-only port of the Python CLI under
// src/agentskills/. It mirrors the observable behaviour of bootstrap.py,
// list.py and link.py, and adds a doctor command modelled on jwa-tobrew.
//
// Boundary contract: this CLI never executes skill content. Scripts inside
// skills/<name>/scripts/ are copied verbatim and treated as opaque. The CLI
// only ever shells out to `git`. See docs/cli-go-port-briefing.md and ADR
// 0006 in jwa91/homebrew-tap.
package main

import (
	"fmt"
	"os"

	"github.com/jwa91/agentskills/tools/agentskills/cmd"
)

const usage = `agentskills — install and manage agent skills in a project

Usage:
  agentskills <command> [flags]

Commands:
  bootstrap  Copy or symlink skills into <project>/.agents/skills
  list       List available skills from a local or remote repo
  link       Create harness symlinks (.claude, .opencode, .amp) into .agents/skills
  doctor     Verify git, cache dir, target dir and default repo

Run 'agentskills <command> --help' for command-specific flags.

Defaults:
  Repo:  https://github.com/jwa91/agentskills.git (override via --repo-url or $AGENTSKILLS_REPO)
  Ref:   main                                     (override via --ref or $AGENTSKILLS_REF)
  Cache: ~/.cache/agentskills/repos/
`

// Set by GoReleaser via -ldflags.
var (
	version = "dev"
	commit  = "none"
	date    = "unknown"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Fprint(os.Stderr, usage)
		os.Exit(2)
	}

	name := os.Args[1]
	args := os.Args[2:]

	var err error
	switch name {
	case "bootstrap":
		err = cmd.RunBootstrap(args)
	case "list":
		err = cmd.RunList(args)
	case "link":
		err = cmd.RunLink(args)
	case "doctor":
		err = cmd.RunDoctor(args)
	case "version", "-v", "--version":
		fmt.Printf("agentskills %s (commit %s, built %s)\n", version, commit, date)
		return
	case "-h", "--help", "help":
		fmt.Print(usage)
		return
	default:
		fmt.Fprintf(os.Stderr, "unknown command: %q\n\n%s", name, usage)
		os.Exit(2)
	}
	if err != nil {
		fmt.Fprintf(os.Stderr, "%s error: %v\n", name, err)
		os.Exit(1)
	}
}
