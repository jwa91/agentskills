// Package cmd holds the subcommand implementations for the agentskills
// binary. Each file in this package corresponds to one user-visible
// command (bootstrap, list, link, doctor) and ports its Python sibling
// under src/agentskills/ with the same flag surface and exit semantics.
package cmd

import (
	"flag"
	"fmt"
	"os"
	"strings"
)

// SubFlagSet returns a flag set with a friendly Usage banner.
func SubFlagSet(name, summary string) *flag.FlagSet {
	fs := flag.NewFlagSet(name, flag.ExitOnError)
	fs.Usage = func() {
		fmt.Fprintf(os.Stderr, "agentskills %s — %s\n\nFlags:\n", name, summary)
		fs.PrintDefaults()
	}
	return fs
}

// ParseFlags reorders args so flags can appear after positionals.
//
// Stdlib `flag` stops at the first non-flag token; this helper splits
// args into a flag stream and a positional stream so interleaved usage
// works the way most CLIs do. Anything after "--" is literal.
func ParseFlags(fs *flag.FlagSet, args []string) error {
	isBool := func(name string) bool {
		f := fs.Lookup(name)
		if f == nil {
			return false
		}
		if bf, ok := f.Value.(interface{ IsBoolFlag() bool }); ok && bf.IsBoolFlag() {
			return true
		}
		return false
	}
	var flags, pos []string
	for i := 0; i < len(args); i++ {
		a := args[i]
		if a == "--" {
			pos = append(pos, args[i+1:]...)
			break
		}
		if strings.HasPrefix(a, "-") && a != "-" {
			flags = append(flags, a)
			n := strings.TrimLeft(a, "-")
			if eq := strings.IndexByte(n, '='); eq >= 0 {
				continue
			}
			if !isBool(n) && i+1 < len(args) {
				flags = append(flags, args[i+1])
				i++
			}
		} else {
			pos = append(pos, a)
		}
	}
	return fs.Parse(append(flags, pos...))
}

// repeatableList is a flag.Value implementation that captures repeated
// invocations of the same flag into a slice (mirrors argparse action="append").
type repeatableList struct {
	values *[]string
}

func newRepeatableList(target *[]string) *repeatableList { return &repeatableList{values: target} }

func (r *repeatableList) Set(v string) error {
	*r.values = append(*r.values, v)
	return nil
}

func (r *repeatableList) String() string {
	if r == nil || r.values == nil {
		return ""
	}
	return strings.Join(*r.values, ",")
}

// SplitCommaList parses a slice of raw flag values (each of which may
// contain comma-separated entries) into a deduplicated, order-preserving
// list. It is the Go equivalent of the Python `parse_skill_list` / `parse_harness_list`
// helpers and is exported so tests can exercise it directly.
func SplitCommaList(raw []string) []string {
	out := []string{}
	seen := map[string]bool{}
	for _, r := range raw {
		for _, part := range strings.Split(r, ",") {
			p := strings.TrimSpace(part)
			if p == "" || seen[p] {
				continue
			}
			seen[p] = true
			out = append(out, p)
		}
	}
	return out
}

// envOr returns the value of the named env var, or fallback when unset.
func envOr(name, fallback string) string {
	if v := os.Getenv(name); v != "" {
		return v
	}
	return fallback
}

// DefaultRepoURL returns the upstream skill repository URL, honoring
// AGENTSKILLS_REPO.
func DefaultRepoURL() string {
	return envOr("AGENTSKILLS_REPO", "https://github.com/jwa91/agentskills.git")
}

// DefaultRef returns the default git ref, honoring AGENTSKILLS_REF.
func DefaultRef() string {
	return envOr("AGENTSKILLS_REF", "main")
}
