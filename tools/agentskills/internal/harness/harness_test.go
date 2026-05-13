package harness

import (
	"os"
	"path/filepath"
	"reflect"
	"sort"
	"testing"
)

func TestLoadEmbedded(t *testing.T) {
	c, err := LoadEmbedded()
	if err != nil {
		t.Fatal(err)
	}
	if c.CanonicalSkillsDir != ".agents/skills" {
		t.Errorf("canonical = %q", c.CanonicalSkillsDir)
	}
	want := []string{"amp", "anthropic", "opencode"}
	got := c.Names()
	sort.Strings(got)
	if !reflect.DeepEqual(got, want) {
		t.Errorf("names = %v, want %v", got, want)
	}
	a, ok := c.Resolve("anthropic")
	if !ok {
		t.Fatal("anthropic adapter not found")
	}
	if a.RelativeLinkPath != ".claude/skills" {
		t.Errorf("anthropic.RelativeLinkPath = %q", a.RelativeLinkPath)
	}
	if _, ok := c.Resolve("nope"); ok {
		t.Errorf("Resolve(nope) should return false")
	}
}

func TestLoadFromBytesInvalid(t *testing.T) {
	if _, err := LoadFromBytes([]byte(`{}`)); err == nil {
		t.Errorf("expected error on empty config")
	}
	if _, err := LoadFromBytes([]byte(`not json`)); err == nil {
		t.Errorf("expected parse error")
	}
}

func TestLinkCreatesSymlink(t *testing.T) {
	root := t.TempDir()
	canonical := filepath.Join(root, ".agents", "skills")
	if err := os.MkdirAll(canonical, 0o755); err != nil {
		t.Fatal(err)
	}
	linkPath := filepath.Join(root, ".claude", "skills")
	relTarget, err := filepath.Rel(filepath.Dir(linkPath), canonical)
	if err != nil {
		t.Fatal(err)
	}

	res, err := Link("anthropic", linkPath, relTarget, LinkOptions{})
	if err != nil {
		t.Fatal(err)
	}
	if res.Action != "linked" {
		t.Errorf("action = %q", res.Action)
	}
	if fi, err := os.Lstat(linkPath); err != nil || fi.Mode()&os.ModeSymlink == 0 {
		t.Errorf("symlink not created: %v", err)
	}

	// Second call should skip with the matching target.
	res, err = Link("anthropic", linkPath, relTarget, LinkOptions{})
	if err != nil {
		t.Fatal(err)
	}
	if res.Action != "skip" {
		t.Errorf("expected skip on idempotent re-link, got %s", res.Action)
	}

	// Force replacement to a different target.
	other := filepath.Join(root, "other-dir")
	if err := os.MkdirAll(other, 0o755); err != nil {
		t.Fatal(err)
	}
	otherRel, _ := filepath.Rel(filepath.Dir(linkPath), other)
	if _, err := Link("anthropic", linkPath, otherRel, LinkOptions{}); err == nil {
		t.Errorf("expected error on mismatched target without --force")
	}
	if _, err := Link("anthropic", linkPath, otherRel, LinkOptions{Force: true}); err != nil {
		t.Errorf("force replace failed: %v", err)
	}
}

func TestLinkDryRun(t *testing.T) {
	root := t.TempDir()
	canonical := filepath.Join(root, ".agents", "skills")
	if err := os.MkdirAll(canonical, 0o755); err != nil {
		t.Fatal(err)
	}
	linkPath := filepath.Join(root, ".claude", "skills")
	rel, _ := filepath.Rel(filepath.Dir(linkPath), canonical)
	res, err := Link("anthropic", linkPath, rel, LinkOptions{DryRun: true})
	if err != nil {
		t.Fatal(err)
	}
	if res.Action != "plan" {
		t.Errorf("action = %q", res.Action)
	}
	if _, err := os.Lstat(linkPath); err == nil {
		t.Errorf("dry-run should not create link")
	}
}
