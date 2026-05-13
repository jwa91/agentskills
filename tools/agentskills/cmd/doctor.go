package cmd

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/jwa91/agentskills/tools/agentskills/internal/harness"
	"github.com/jwa91/agentskills/tools/agentskills/internal/skillrepo"
)

// RunDoctor verifies that the host can run the rest of the CLI.
//
// Mirrors the shape of `jwa-tobrew doctor`: each check prints a ✓/!/✗
// line and the command exits non-zero only when a fatal check fails.
func RunDoctor(args []string) error {
	fs := SubFlagSet("doctor", "verify git, cache dir, target dir and default repo")
	var (
		project = fs.String("project", "", "if set, verify <project>/.agents/skills is writable")
	)
	if err := ParseFlags(fs, args); err != nil {
		return err
	}

	banner("agentskills doctor")
	failed := 0

	// 1. git on PATH.
	if _, err := exec.LookPath("git"); err != nil {
		fail("git not found on PATH — `brew install git`")
		failed++
	} else {
		ok("git installed")
	}

	// 2. Cache dir reachable and writable.
	cache, err := skillrepo.DefaultCacheDir()
	if err != nil {
		fail("cannot resolve cache dir: %v", err)
		failed++
	} else if err := ensureWritableDir(cache); err != nil {
		fail("cache dir not writable (%s): %v", cache, err)
		failed++
	} else {
		ok("cache dir writable at %s", cache)
	}

	// 3. Embedded harness adapter table parses.
	if cfg, err := harness.LoadEmbedded(); err != nil {
		fail("embedded harness adapter table failed to parse: %v", err)
		failed++
	} else {
		ok("harness adapters loaded (%d adapter(s): %s)", len(cfg.Adapters), strings.Join(cfg.Names(), ", "))
	}

	// 4. Optional: project target writable.
	if *project != "" {
		abs, err := filepath.Abs(expandHome(*project))
		if err != nil {
			fail("resolve project path: %v", err)
			failed++
		} else {
			target := filepath.Join(abs, ".agents", "skills")
			if err := ensureWritableDir(target); err != nil {
				fail("project skills dir not writable (%s): %v", target, err)
				failed++
			} else {
				ok("project skills dir writable at %s", target)
			}
		}
	} else {
		hint("pass --project <path> to check that .agents/skills is writable")
	}

	// 5. Default repo URL resolves to *something* (just a string check —
	//    we don't want to perform a network ls-remote inside doctor,
	//    which would slow it down and require connectivity).
	url := DefaultRepoURL()
	if url == "" {
		fail("default repo URL is empty")
		failed++
	} else {
		ok("default repo URL: %s", url)
		hint("ref: %s", DefaultRef())
	}

	if failed > 0 {
		return fmt.Errorf("%d check(s) failed", failed)
	}
	info("doctor: all checks passed")
	return nil
}

func ensureWritableDir(path string) error {
	if err := os.MkdirAll(path, 0o755); err != nil {
		return err
	}
	probe := filepath.Join(path, ".agentskills-doctor-probe")
	f, err := os.Create(probe)
	if err != nil {
		return err
	}
	_ = f.Close()
	return os.Remove(probe)
}
