// Package skillrepo handles the cache, clone, and discovery of skill
// directories that the agentskills CLI manages.
//
// Skills live under <repo>/skills/<name>/ for "own" skills and under
// <repo>/skills/curated/<name>/ for curated skills. Own skills shadow
// curated skills with the same name. A directory only counts as a skill
// when it contains a SKILL.md file at its root.
//
// The package treats every byte under a skill directory as opaque content:
// it copies files verbatim, never executes anything, and only shells out
// to `git` for clone/fetch/checkout.
package skillrepo

import (
	"errors"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strings"
)

// CuratedDir is the subdirectory under skills/ that holds curated skills.
const CuratedDir = "curated"

// SkillManifest is the filename that marks a directory as a skill.
const SkillManifest = "SKILL.md"

// DefaultCacheDir returns ~/.cache/agentskills/repos, matching the Python CLI.
func DefaultCacheDir() (string, error) {
	home, err := os.UserHomeDir()
	if err != nil {
		return "", err
	}
	return filepath.Join(home, ".cache", "agentskills", "repos"), nil
}

// CacheNameForRepo derives a filesystem-safe cache directory name from a
// git URL, matching the Python `repo_cache_name` helper.
//
// Behaviour:
//   - strips trailing slashes
//   - keeps the final URL segment
//   - drops a trailing `.git`
//   - replaces any rune outside [A-Za-z0-9._-] with '-'
//   - falls back to "skills-repo" when the result is empty
func CacheNameForRepo(repoURL string) string {
	trimmed := strings.TrimRight(repoURL, "/")
	idx := strings.LastIndex(trimmed, "/")
	name := trimmed
	if idx >= 0 {
		name = trimmed[idx+1:]
	}
	name = strings.TrimSuffix(name, ".git")
	var b strings.Builder
	for _, r := range name {
		switch {
		case (r >= 'a' && r <= 'z'), (r >= 'A' && r <= 'Z'), (r >= '0' && r <= '9'),
			r == '-', r == '_', r == '.':
			b.WriteRune(r)
		default:
			b.WriteRune('-')
		}
	}
	out := b.String()
	if out == "" {
		return "skills-repo"
	}
	return out
}

// CloneOrUpdate clones the given repo into <cacheDir>/<derivedName> if it
// does not exist yet, otherwise fetches updates. It then checks out the
// requested ref and tries a fast-forward pull. It returns the local repo
// path.
//
// The function only invokes `git` — no other tooling is consulted.
func CloneOrUpdate(repoURL, ref, cacheDir string) (string, error) {
	if err := os.MkdirAll(cacheDir, 0o755); err != nil {
		return "", fmt.Errorf("create cache dir: %w", err)
	}
	repoPath := filepath.Join(cacheDir, CacheNameForRepo(repoURL))

	if _, err := os.Stat(repoPath); errors.Is(err, os.ErrNotExist) {
		if _, _, err := runGit("", "clone", repoURL, repoPath); err != nil {
			return "", err
		}
	} else if err != nil {
		return "", err
	} else {
		if _, _, err := runGit(repoPath, "fetch", "--all", "--tags", "--prune"); err != nil {
			return "", err
		}
	}

	if _, _, err := runGit(repoPath, "checkout", ref); err != nil {
		return "", err
	}

	_, stderr, err := runGitNoCheck(repoPath, "pull", "--ff-only")
	if err != nil && !strings.Contains(strings.ToLower(stderr), "not currently on a branch") {
		fmt.Fprintf(os.Stderr, "warning: pull skipped: %s\n", strings.TrimSpace(stderr))
	}

	return repoPath, nil
}

// runGit runs `git <args...>` in cwd and returns (stdout, stderr) on success.
func runGit(cwd string, args ...string) (string, string, error) {
	stdout, stderr, err := runGitNoCheck(cwd, args...)
	if err != nil {
		joined := strings.Join(append([]string{"git"}, args...), " ")
		return stdout, stderr, fmt.Errorf("command failed (%s): %s", joined, strings.TrimSpace(stderr))
	}
	return stdout, stderr, nil
}

func runGitNoCheck(cwd string, args ...string) (string, string, error) {
	c := exec.Command("git", args...)
	if cwd != "" {
		c.Dir = cwd
	}
	var stdout, stderr strings.Builder
	c.Stdout = &stdout
	c.Stderr = &stderr
	err := c.Run()
	return stdout.String(), stderr.String(), err
}

// DiscoverAll returns every skill name found under skillsRoot.
// Own skills (under skillsRoot directly) take precedence over curated
// skills with the same name.
func DiscoverAll(skillsRoot string) []string {
	own, curated := Categorize(skillsRoot)
	return append(own, curated...)
}

// Categorize returns (ownNames, curatedNames). Own skills come first and
// shadow any curated entry with the same name.
func Categorize(skillsRoot string) ([]string, []string) {
	if _, err := os.Stat(skillsRoot); err != nil {
		return nil, nil
	}
	own := skillNamesIn(skillsRoot, func(name string) bool { return name != CuratedDir })

	curatedRoot := filepath.Join(skillsRoot, CuratedDir)
	curated := []string{}
	if fi, err := os.Stat(curatedRoot); err == nil && fi.IsDir() {
		ownSet := map[string]bool{}
		for _, n := range own {
			ownSet[n] = true
		}
		for _, n := range skillNamesIn(curatedRoot, func(string) bool { return true }) {
			if !ownSet[n] {
				curated = append(curated, n)
			}
		}
	}
	return own, curated
}

func skillNamesIn(root string, filter func(string) bool) []string {
	entries, err := os.ReadDir(root)
	if err != nil {
		return nil
	}
	out := []string{}
	for _, e := range entries {
		if !e.IsDir() || !filter(e.Name()) {
			continue
		}
		if _, err := os.Stat(filepath.Join(root, e.Name(), SkillManifest)); err != nil {
			continue
		}
		out = append(out, e.Name())
	}
	sort.Strings(out)
	return out
}

// ResolveSkillDir returns the on-disk path for the given skill name,
// checking own first and then curated.
func ResolveSkillDir(skillsRoot, name string) (string, error) {
	own := filepath.Join(skillsRoot, name)
	if isSkillDir(own) {
		return own, nil
	}
	curated := filepath.Join(skillsRoot, CuratedDir, name)
	if isSkillDir(curated) {
		return curated, nil
	}
	return "", fmt.Errorf("skill not found: %s (checked %s and %s)", name, own, curated)
}

func isSkillDir(path string) bool {
	fi, err := os.Stat(path)
	if err != nil || !fi.IsDir() {
		return false
	}
	_, err = os.Stat(filepath.Join(path, SkillManifest))
	return err == nil
}

// CopySkill copies the skill tree at src into dst.
// Contents are copied byte-for-byte; nothing is executed or interpreted.
func CopySkill(src, dst string) error {
	return filepath.Walk(src, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		rel, err := filepath.Rel(src, path)
		if err != nil {
			return err
		}
		target := filepath.Join(dst, rel)

		switch {
		case info.Mode()&os.ModeSymlink != 0:
			link, err := os.Readlink(path)
			if err != nil {
				return err
			}
			if err := os.MkdirAll(filepath.Dir(target), 0o755); err != nil {
				return err
			}
			return os.Symlink(link, target)
		case info.IsDir():
			return os.MkdirAll(target, info.Mode().Perm())
		default:
			return copyFile(path, target, info.Mode().Perm())
		}
	})
}

func copyFile(src, dst string, mode os.FileMode) error {
	in, err := os.Open(src)
	if err != nil {
		return err
	}
	defer in.Close()
	if err := os.MkdirAll(filepath.Dir(dst), 0o755); err != nil {
		return err
	}
	out, err := os.OpenFile(dst, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, mode)
	if err != nil {
		return err
	}
	defer out.Close()
	_, err = io.Copy(out, in)
	return err
}

// RemovePath removes a file, symlink, or directory tree at path.
func RemovePath(path string) error {
	fi, err := os.Lstat(path)
	if err != nil {
		if errors.Is(err, os.ErrNotExist) {
			return nil
		}
		return err
	}
	if fi.Mode()&os.ModeSymlink != 0 || !fi.IsDir() {
		return os.Remove(path)
	}
	return os.RemoveAll(path)
}

// InstallSkill places source content at destination, respecting mode.
// When mode is "symlink", a symlink to the resolved source path is created.
// When mode is anything else (treated as "copy"), the directory is copied.
func InstallSkill(skillName, sourceRoot, destinationRoot, mode string, force bool) (string, error) {
	src, err := ResolveSkillDir(sourceRoot, skillName)
	if err != nil {
		return "", err
	}
	dst := filepath.Join(destinationRoot, skillName)
	if _, err := os.Lstat(dst); err == nil {
		if !force {
			return "", fmt.Errorf("destination already exists: %s (use --force to replace)", dst)
		}
		if err := RemovePath(dst); err != nil {
			return "", err
		}
	} else if !errors.Is(err, os.ErrNotExist) {
		return "", err
	}

	if mode == "symlink" {
		absSrc, err := filepath.Abs(src)
		if err != nil {
			return "", err
		}
		if err := os.MkdirAll(filepath.Dir(dst), 0o755); err != nil {
			return "", err
		}
		if err := os.Symlink(absSrc, dst); err != nil {
			return "", err
		}
		return dst, nil
	}
	if err := CopySkill(src, dst); err != nil {
		return "", err
	}
	return dst, nil
}
