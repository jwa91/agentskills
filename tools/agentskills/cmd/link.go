package cmd

import (
	"fmt"
	"os"
	"path/filepath"
	"sort"

	"github.com/jwa91/agentskills/tools/agentskills/internal/harness"
)

// RunLink creates harness symlinks for a project.
func RunLink(args []string) error {
	fs := SubFlagSet("link", "create harness symlinks (.claude, .opencode, .amp) into .agents/skills")
	var (
		project    = fs.String("project", "", "project directory containing .agents/skills (required)")
		configPath = fs.String("config", "", "adapter config JSON path (default: embedded)")
		force      = fs.Bool("force", false, "replace existing non-matching link/path")
		dryRun     = fs.Bool("dry-run", false, "print planned actions without writing changes")
	)
	var harnessFlag []string
	fs.Var(newRepeatableList(&harnessFlag), "harness", "harness name(s); repeat or comma-separate (default: all)")

	if err := ParseFlags(fs, args); err != nil {
		return err
	}

	if *project == "" {
		return fmt.Errorf("--project is required")
	}
	projectRoot, err := filepath.Abs(expandHome(*project))
	if err != nil {
		return err
	}

	var cfg *harness.Config
	if *configPath != "" {
		data, err := os.ReadFile(expandHome(*configPath))
		if err != nil {
			return fmt.Errorf("read config: %w", err)
		}
		cfg, err = harness.LoadFromBytes(data)
		if err != nil {
			return err
		}
	} else {
		cfg, err = harness.LoadEmbedded()
		if err != nil {
			return err
		}
	}

	canonicalDir := filepath.Join(projectRoot, cfg.CanonicalSkillsDir)
	if _, err := os.Stat(canonicalDir); err != nil {
		return fmt.Errorf("canonical skills directory is missing: %s. install skills first via `agentskills bootstrap`", canonicalDir)
	}

	selected := SplitCommaList(harnessFlag)
	names := selected
	if len(names) == 0 {
		names = cfg.Names()
	} else {
		sort.Strings(names) // deterministic order
	}

	var unknown []string
	for _, n := range names {
		if _, ok := cfg.Resolve(n); !ok {
			unknown = append(unknown, n)
		}
	}
	if len(unknown) > 0 {
		return fmt.Errorf("unknown harness(es): %v", unknown)
	}

	fmt.Printf("project: %s\n", projectRoot)
	fmt.Printf("canonical: %s\n", canonicalDir)
	fmt.Printf("dry_run: %v\n", *dryRun)

	for _, n := range names {
		ad, _ := cfg.Resolve(n)
		if ad.RelativeLinkPath == "" {
			return fmt.Errorf("adapter %s is missing relative_link_path", n)
		}
		linkPath := filepath.Join(projectRoot, ad.RelativeLinkPath)
		relTarget, err := filepath.Rel(filepath.Dir(linkPath), canonicalDir)
		if err != nil {
			return err
		}
		res, err := harness.Link(n, linkPath, relTarget, harness.LinkOptions{Force: *force, DryRun: *dryRun})
		if err != nil {
			return err
		}
		fmt.Println(res.Message)
	}

	fmt.Println("done: optional harness links are configured.")
	return nil
}
