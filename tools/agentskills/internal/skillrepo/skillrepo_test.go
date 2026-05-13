package skillrepo

import (
	"os"
	"path/filepath"
	"reflect"
	"testing"
)

func TestCacheNameForRepo(t *testing.T) {
	cases := []struct {
		in, want string
	}{
		{"https://github.com/jwa91/agentskills.git", "agentskills"},
		{"https://github.com/jwa91/agentskills.git/", "agentskills"},
		{"git@github.com:jwa91/agentskills.git", "agentskills"},
		{"https://example.com/some/path/my-repo", "my-repo"},
		{"https://example.com/My_Skills.v2.git", "My_Skills.v2"},
		{"https://example.com/Hello World/", "Hello-World"},
		{"", "skills-repo"},
		{"/", "skills-repo"},
		{"https://example.com/weird&chars$.git", "weird-chars-"},
	}
	for _, c := range cases {
		got := CacheNameForRepo(c.in)
		if got != c.want {
			t.Errorf("CacheNameForRepo(%q) = %q, want %q", c.in, got, c.want)
		}
	}
}

// makeSkill writes a minimal SKILL.md so the directory counts as a skill.
func makeSkill(t *testing.T, dir string) {
	t.Helper()
	if err := os.MkdirAll(dir, 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(dir, SkillManifest), []byte("---\nname: x\n---\n"), 0o644); err != nil {
		t.Fatal(err)
	}
}

func TestDiscoverOwnAndCurated(t *testing.T) {
	root := t.TempDir()
	skills := filepath.Join(root, "skills")
	makeSkill(t, filepath.Join(skills, "alpha"))
	makeSkill(t, filepath.Join(skills, "beta"))
	makeSkill(t, filepath.Join(skills, "curated", "gamma"))
	// Curated entry shadowed by own.
	makeSkill(t, filepath.Join(skills, "curated", "alpha"))
	// A directory without SKILL.md should be ignored.
	if err := os.MkdirAll(filepath.Join(skills, "not-a-skill"), 0o755); err != nil {
		t.Fatal(err)
	}

	own, curated := Categorize(skills)
	if !reflect.DeepEqual(own, []string{"alpha", "beta"}) {
		t.Errorf("own = %v, want [alpha beta]", own)
	}
	if !reflect.DeepEqual(curated, []string{"gamma"}) {
		t.Errorf("curated = %v, want [gamma]", curated)
	}
	all := DiscoverAll(skills)
	if !reflect.DeepEqual(all, []string{"alpha", "beta", "gamma"}) {
		t.Errorf("DiscoverAll = %v", all)
	}
}

func TestResolveSkillDirOwnShadowsCurated(t *testing.T) {
	root := t.TempDir()
	skills := filepath.Join(root, "skills")
	makeSkill(t, filepath.Join(skills, "alpha"))
	makeSkill(t, filepath.Join(skills, "curated", "alpha"))
	makeSkill(t, filepath.Join(skills, "curated", "gamma"))

	p, err := ResolveSkillDir(skills, "alpha")
	if err != nil {
		t.Fatal(err)
	}
	if p != filepath.Join(skills, "alpha") {
		t.Errorf("alpha resolved to %s", p)
	}
	p, err = ResolveSkillDir(skills, "gamma")
	if err != nil {
		t.Fatal(err)
	}
	if p != filepath.Join(skills, "curated", "gamma") {
		t.Errorf("gamma resolved to %s", p)
	}
	if _, err := ResolveSkillDir(skills, "missing"); err == nil {
		t.Errorf("expected error for missing skill")
	}
}

func TestInstallSkillCopy(t *testing.T) {
	root := t.TempDir()
	skills := filepath.Join(root, "skills")
	makeSkill(t, filepath.Join(skills, "alpha"))
	// Add a scripts file to verify opaque copy.
	scriptsDir := filepath.Join(skills, "alpha", "scripts")
	if err := os.MkdirAll(scriptsDir, 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(scriptsDir, "do.py"), []byte("print(1)\n"), 0o755); err != nil {
		t.Fatal(err)
	}

	dst := filepath.Join(root, "project", ".agents", "skills")
	if err := os.MkdirAll(dst, 0o755); err != nil {
		t.Fatal(err)
	}
	out, err := InstallSkill("alpha", skills, dst, "copy", false)
	if err != nil {
		t.Fatal(err)
	}
	if out != filepath.Join(dst, "alpha") {
		t.Errorf("installed path = %s", out)
	}
	if _, err := os.Stat(filepath.Join(out, "SKILL.md")); err != nil {
		t.Errorf("SKILL.md missing: %v", err)
	}
	if _, err := os.Stat(filepath.Join(out, "scripts", "do.py")); err != nil {
		t.Errorf("scripts/do.py missing: %v", err)
	}

	// Re-installing without --force should fail.
	if _, err := InstallSkill("alpha", skills, dst, "copy", false); err == nil {
		t.Errorf("expected error when destination exists without --force")
	}
	// With --force it should succeed.
	if _, err := InstallSkill("alpha", skills, dst, "copy", true); err != nil {
		t.Errorf("expected force install to succeed, got %v", err)
	}
}

func TestInstallSkillSymlink(t *testing.T) {
	root := t.TempDir()
	skills := filepath.Join(root, "skills")
	makeSkill(t, filepath.Join(skills, "alpha"))

	dst := filepath.Join(root, "project", ".agents", "skills")
	if err := os.MkdirAll(dst, 0o755); err != nil {
		t.Fatal(err)
	}
	out, err := InstallSkill("alpha", skills, dst, "symlink", false)
	if err != nil {
		t.Fatal(err)
	}
	fi, err := os.Lstat(out)
	if err != nil {
		t.Fatal(err)
	}
	if fi.Mode()&os.ModeSymlink == 0 {
		t.Errorf("expected symlink at %s", out)
	}
}
