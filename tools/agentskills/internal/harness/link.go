package harness

import (
	"errors"
	"fmt"
	"os"
	"path/filepath"
)

// LinkResult describes the outcome of a single harness link attempt.
type LinkResult struct {
	Name     string
	LinkPath string
	Target   string // relative target from link's parent dir
	Action   string // "linked", "skip", "plan"
	Message  string
}

// LinkOptions controls the Link function.
type LinkOptions struct {
	Force  bool
	DryRun bool
}

// Link creates (or validates) a single symlink at linkPath pointing to a
// path relative to linkPath's parent directory.
//
// Behaviour mirrors the Python `_link_harness` helper:
//   - if linkPath is already a symlink to relativeTarget: skip
//   - if linkPath is a symlink to something else: error unless force
//   - if linkPath exists as file/dir: error unless force
//   - dryRun reports the planned action and writes nothing
func Link(name, linkPath, relativeTarget string, opts LinkOptions) (LinkResult, error) {
	res := LinkResult{Name: name, LinkPath: linkPath, Target: relativeTarget}

	fi, lerr := os.Lstat(linkPath)
	switch {
	case lerr == nil && fi.Mode()&os.ModeSymlink != 0:
		existing, err := os.Readlink(linkPath)
		if err != nil {
			return res, err
		}
		if existing == relativeTarget {
			res.Action = "skip"
			res.Message = fmt.Sprintf("skip: %s already linked (%s -> %s)", name, linkPath, relativeTarget)
			return res, nil
		}
		if !opts.Force {
			return res, fmt.Errorf("link already exists for %s with different target: %s -> %s (use --force to replace)", name, linkPath, existing)
		}
		if !opts.DryRun {
			if err := os.Remove(linkPath); err != nil {
				return res, err
			}
		}
	case lerr == nil:
		// regular file or directory at link path
		if !opts.Force {
			return res, fmt.Errorf("path already exists for %s: %s (use --force to replace)", name, linkPath)
		}
		if !opts.DryRun {
			if fi.IsDir() {
				if err := os.RemoveAll(linkPath); err != nil {
					return res, err
				}
			} else {
				if err := os.Remove(linkPath); err != nil {
					return res, err
				}
			}
		}
	case !errors.Is(lerr, os.ErrNotExist):
		return res, lerr
	}

	if opts.DryRun {
		res.Action = "plan"
		res.Message = fmt.Sprintf("plan: link %s (%s -> %s)", name, linkPath, relativeTarget)
		return res, nil
	}

	if err := os.MkdirAll(filepath.Dir(linkPath), 0o755); err != nil {
		return res, err
	}
	if err := os.Symlink(relativeTarget, linkPath); err != nil {
		return res, err
	}
	res.Action = "linked"
	res.Message = fmt.Sprintf("linked: %s (%s -> %s)", name, linkPath, relativeTarget)
	return res, nil
}
