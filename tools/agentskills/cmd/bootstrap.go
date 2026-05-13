package cmd

import (
	"bufio"
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"strings"

	"github.com/jwa91/agentskills/tools/agentskills/internal/skillrepo"
)

const projectSkillsRel = ".agents/skills"

// RunBootstrap is the entrypoint for `agentskills bootstrap`.
func RunBootstrap(args []string) error {
	fs := SubFlagSet("bootstrap", "install one or more skills into a project's .agents/skills directory")
	var (
		project    = fs.String("project", ".", "target project path")
		mode       = fs.String("mode", "copy", "install mode: copy (safest) or symlink")
		force      = fs.Bool("force", false, "replace destination skill if it already exists")
		repoURL    = fs.String("repo-url", "", "git URL to clone/pull from (defaults to $AGENTSKILLS_REPO or upstream)")
		repoPath   = fs.String("repo-path", "", "use a local repo path instead of cloning")
		ref        = fs.String("ref", "", "git branch or tag when --repo-url is used (defaults to $AGENTSKILLS_REF or 'main')")
		cacheDir   = fs.String("cache-dir", "", "clone cache directory")
		installAll = fs.Bool("all", false, "install all available skills without prompting")
	)
	var skillFlag []string
	fs.Var(newRepeatableList(&skillFlag), "skill", "skill name(s); repeat or comma-separate")

	if err := ParseFlags(fs, args); err != nil {
		return err
	}

	if *repoURL != "" && *repoPath != "" {
		return fmt.Errorf("use either --repo-path or --repo-url, not both")
	}
	if *mode != "copy" && *mode != "symlink" {
		return fmt.Errorf("--mode must be 'copy' or 'symlink' (got %q)", *mode)
	}

	resolvedCache := *cacheDir
	if resolvedCache == "" {
		c, err := skillrepo.DefaultCacheDir()
		if err != nil {
			return err
		}
		resolvedCache = c
	}

	repoRoot, err := resolveRepoRoot(*repoURL, *repoPath, *ref, resolvedCache)
	if err != nil {
		return err
	}

	skillsRoot := filepath.Join(repoRoot, "skills")
	available := skillrepo.DiscoverAll(skillsRoot)
	if len(available) == 0 {
		return fmt.Errorf("no skills found under: %s", skillsRoot)
	}

	requested := SplitCommaList(skillFlag)
	var selected []string
	switch {
	case len(requested) > 0:
		selected = requested
	case *installAll:
		selected = available
	default:
		picked, err := pickSkillsInteractive(skillsRoot)
		if err != nil {
			return err
		}
		selected = picked
	}

	availSet := map[string]bool{}
	for _, n := range available {
		availSet[n] = true
	}
	var unknown []string
	for _, n := range selected {
		if !availSet[n] {
			unknown = append(unknown, n)
		}
	}
	if len(unknown) > 0 {
		return fmt.Errorf("unknown skill(s): %s. available: %s",
			strings.Join(unknown, ", "), strings.Join(available, ", "))
	}

	absProject, err := filepath.Abs(expandHome(*project))
	if err != nil {
		return err
	}
	if err := os.MkdirAll(absProject, 0o755); err != nil {
		return err
	}
	destinationRoot := filepath.Join(absProject, projectSkillsRel)
	if err := os.MkdirAll(destinationRoot, 0o755); err != nil {
		return err
	}

	if *mode == "symlink" {
		fmt.Fprintln(os.Stderr, "warning: symlink mode creates links that resolve outside the project directory. This may cause permission prompts in Claude Code for every file read. Use --mode copy to avoid this.")
	}

	var installed []string
	for _, name := range selected {
		p, err := skillrepo.InstallSkill(name, skillsRoot, destinationRoot, *mode, *force)
		if err != nil {
			return err
		}
		installed = append(installed, p)
	}

	fmt.Printf("repo: %s\n", repoRoot)
	fmt.Printf("project: %s\n", absProject)
	fmt.Printf("mode: %s\n", *mode)
	fmt.Println("installed:")
	for _, p := range installed {
		fmt.Printf("  - %s\n", p)
	}
	fmt.Println("next: run optional harness links with `agentskills link` if needed.")
	return nil
}

func resolveRepoRoot(repoURL, repoPath, ref, cacheDir string) (string, error) {
	if repoPath != "" {
		abs, err := filepath.Abs(expandHome(repoPath))
		if err != nil {
			return "", err
		}
		if _, err := os.Stat(abs); err != nil {
			return "", fmt.Errorf("repo path does not exist: %s", abs)
		}
		return abs, nil
	}

	url := repoURL
	if url == "" {
		// Only fall through to clone if user explicitly asked (via --repo-url
		// or env). Otherwise we assume the user is running from inside a
		// clone of jwa91/agentskills and try the source tree.
		if env := os.Getenv("AGENTSKILLS_REPO"); env != "" {
			url = env
		}
	}

	if url == "" {
		if root, ok := findLocalRepoRoot(); ok {
			return root, nil
		}
		// Fall back to default upstream URL.
		url = DefaultRepoURL()
	}

	r := ref
	if r == "" {
		r = DefaultRef()
	}
	return skillrepo.CloneOrUpdate(url, r, cacheDir)
}

// findLocalRepoRoot walks up from cwd looking for a skills/ directory.
// This matches the Python `REPO_ROOT` heuristic: when running from within
// the agentskills checkout, prefer the local tree over a network clone.
func findLocalRepoRoot() (string, bool) {
	cwd, err := os.Getwd()
	if err != nil {
		return "", false
	}
	dir := cwd
	for i := 0; i < 8; i++ {
		if fi, err := os.Stat(filepath.Join(dir, "skills")); err == nil && fi.IsDir() {
			return dir, true
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			break
		}
		dir = parent
	}
	return "", false
}

func expandHome(p string) string {
	if strings.HasPrefix(p, "~") {
		if home, err := os.UserHomeDir(); err == nil {
			return filepath.Join(home, strings.TrimPrefix(p, "~"))
		}
	}
	return p
}

// pickSkillsInteractive is a tiny stdlib-only TTY picker. The user types
// space- or comma-separated indices, optionally a/A to toggle all.
// It deliberately stays minimal — the briefing tells us the picker should
// be a deliberate choice, not a default.
func pickSkillsInteractive(skillsRoot string) ([]string, error) {
	if !isStdinTTY() {
		return nil, fmt.Errorf("no skills specified. Use --skill <name>, --all, or `agentskills list` to see available skills")
	}
	own, curated := skillrepo.Categorize(skillsRoot)
	if len(own)+len(curated) == 0 {
		return nil, fmt.Errorf("no skills found under: %s", skillsRoot)
	}
	type row struct {
		name    string
		curated bool
	}
	var rows []row
	for _, n := range own {
		rows = append(rows, row{n, false})
	}
	for _, n := range curated {
		rows = append(rows, row{n, true})
	}

	fmt.Fprintln(os.Stderr, "Available skills:")
	for i, r := range rows {
		label := r.name
		if r.curated {
			label += " (curated)"
		}
		fmt.Fprintf(os.Stderr, "  %2d) %s\n", i+1, label)
	}
	fmt.Fprintln(os.Stderr, "Enter numbers separated by space or comma (or 'a' for all):")
	fmt.Fprint(os.Stderr, "> ")

	reader := bufio.NewReader(os.Stdin)
	line, err := reader.ReadString('\n')
	if err != nil {
		return nil, fmt.Errorf("read selection: %w", err)
	}
	line = strings.TrimSpace(line)
	if line == "" {
		return nil, fmt.Errorf("no selection")
	}
	if line == "a" || line == "A" {
		out := make([]string, 0, len(rows))
		for _, r := range rows {
			out = append(out, r.name)
		}
		return out, nil
	}

	fields := strings.FieldsFunc(line, func(r rune) bool {
		return r == ',' || r == ' ' || r == '\t'
	})
	seen := map[string]bool{}
	var out []string
	for _, f := range fields {
		idx, err := strconv.Atoi(strings.TrimSpace(f))
		if err != nil {
			return nil, fmt.Errorf("invalid selection %q", f)
		}
		if idx < 1 || idx > len(rows) {
			return nil, fmt.Errorf("selection out of range: %d", idx)
		}
		name := rows[idx-1].name
		if !seen[name] {
			seen[name] = true
			out = append(out, name)
		}
	}
	if len(out) == 0 {
		return nil, fmt.Errorf("no skills selected")
	}
	return out, nil
}

func isStdinTTY() bool {
	fi, err := os.Stdin.Stat()
	if err != nil {
		return false
	}
	return (fi.Mode() & os.ModeCharDevice) != 0
}
