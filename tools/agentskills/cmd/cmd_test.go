package cmd

import (
	"flag"
	"os"
	"reflect"
	"testing"
)

func TestSplitCommaList(t *testing.T) {
	cases := []struct {
		in   []string
		want []string
	}{
		{nil, []string{}},
		{[]string{}, []string{}},
		{[]string{"a"}, []string{"a"}},
		{[]string{"a,b"}, []string{"a", "b"}},
		{[]string{"a", "b", "a"}, []string{"a", "b"}},
		{[]string{"a, b ,c"}, []string{"a", "b", "c"}},
		{[]string{"a,b", "c,a"}, []string{"a", "b", "c"}},
		{[]string{"", " , "}, []string{}},
	}
	for _, c := range cases {
		got := SplitCommaList(c.in)
		if !reflect.DeepEqual(got, c.want) {
			t.Errorf("SplitCommaList(%v) = %v, want %v", c.in, got, c.want)
		}
	}
}

func TestRepeatableListWithFlagSet(t *testing.T) {
	fs := flag.NewFlagSet("test", flag.ContinueOnError)
	var skills []string
	fs.Var(newRepeatableList(&skills), "skill", "")

	args := []string{"--skill", "a", "--skill", "b,c", "--skill", "a"}
	if err := fs.Parse(args); err != nil {
		t.Fatal(err)
	}
	got := SplitCommaList(skills)
	want := []string{"a", "b", "c"}
	if !reflect.DeepEqual(got, want) {
		t.Errorf("got %v, want %v", got, want)
	}
}

func TestDefaultRepoURL(t *testing.T) {
	t.Setenv("AGENTSKILLS_REPO", "")
	if u := DefaultRepoURL(); u != "https://github.com/jwa91/agentskills.git" {
		t.Errorf("default = %q", u)
	}
	t.Setenv("AGENTSKILLS_REPO", "https://example.com/x.git")
	if u := DefaultRepoURL(); u != "https://example.com/x.git" {
		t.Errorf("env override failed: %q", u)
	}
}

func TestDefaultRef(t *testing.T) {
	t.Setenv("AGENTSKILLS_REF", "")
	if r := DefaultRef(); r != "main" {
		t.Errorf("default = %q", r)
	}
	t.Setenv("AGENTSKILLS_REF", "v1.2.3")
	if r := DefaultRef(); r != "v1.2.3" {
		t.Errorf("override failed: %q", r)
	}
}

func TestParseFlagsReordering(t *testing.T) {
	fs := flag.NewFlagSet("test", flag.ContinueOnError)
	var name string
	fs.StringVar(&name, "name", "", "")
	args := []string{"positional", "--name", "alice"}
	if err := ParseFlags(fs, args); err != nil {
		t.Fatal(err)
	}
	if name != "alice" {
		t.Errorf("name = %q", name)
	}
	if fs.Arg(0) != "positional" {
		t.Errorf("arg(0) = %q", fs.Arg(0))
	}
}

func TestEnvOr(t *testing.T) {
	t.Setenv("AGENTSKILLS_TEST_VAR", "")
	if got := envOr("AGENTSKILLS_TEST_VAR", "fallback"); got != "fallback" {
		t.Errorf("got %q", got)
	}
	_ = os.Setenv("AGENTSKILLS_TEST_VAR", "value")
	defer os.Unsetenv("AGENTSKILLS_TEST_VAR")
	if got := envOr("AGENTSKILLS_TEST_VAR", "fallback"); got != "value" {
		t.Errorf("got %q", got)
	}
}
