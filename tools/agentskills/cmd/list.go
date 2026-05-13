package cmd

import (
	"fmt"
	"os"
	"path/filepath"

	"github.com/jwa91/agentskills/tools/agentskills/internal/skillrepo"
)

// RunList prints the available skills, grouped by own / curated.
func RunList(args []string) error {
	fs := SubFlagSet("list", "list available agent skills")
	var (
		repoPath = fs.String("repo-path", "", "use a local repo path instead of the current directory")
		repoURL  = fs.String("repo-url", "", "git URL to clone/pull from (uses cache)")
		ref      = fs.String("ref", "", "git branch or tag when --repo-url is used")
		cacheDir = fs.String("cache-dir", "", "clone cache directory")
	)
	if err := ParseFlags(fs, args); err != nil {
		return err
	}

	var skillsRoot string
	switch {
	case *repoPath != "":
		abs, err := filepath.Abs(expandHome(*repoPath))
		if err != nil {
			return err
		}
		skillsRoot = filepath.Join(abs, "skills")
	case *repoURL != "" || os.Getenv("AGENTSKILLS_REPO") != "":
		url := *repoURL
		if url == "" {
			url = DefaultRepoURL()
		}
		r := *ref
		if r == "" {
			r = DefaultRef()
		}
		cd := *cacheDir
		if cd == "" {
			c, err := skillrepo.DefaultCacheDir()
			if err != nil {
				return err
			}
			cd = c
		}
		repoRoot, err := skillrepo.CloneOrUpdate(url, r, cd)
		if err != nil {
			return err
		}
		skillsRoot = filepath.Join(repoRoot, "skills")
	default:
		// Default to the local repo root when running from within a clone.
		if root, ok := findLocalRepoRoot(); ok {
			skillsRoot = filepath.Join(root, "skills")
		} else {
			cwd, _ := os.Getwd()
			skillsRoot = filepath.Join(cwd, "skills")
		}
	}

	own, curated := skillrepo.Categorize(skillsRoot)
	if len(own) == 0 && len(curated) == 0 {
		fmt.Printf("No skills found under: %s\n", skillsRoot)
		return fmt.Errorf("no skills found")
	}
	for _, n := range own {
		fmt.Println(n)
	}
	for _, n := range curated {
		fmt.Printf("%s (curated)\n", n)
	}
	return nil
}
