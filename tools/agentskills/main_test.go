package main

import (
	"bytes"
	"strings"
	"testing"
)

func TestRunNoArgsShowsHelpSuccessfully(t *testing.T) {
	var stdout, stderr bytes.Buffer

	code := run(nil, &stdout, &stderr)

	if code != 0 {
		t.Fatalf("exit code = %d, want 0", code)
	}
	if !strings.Contains(stdout.String(), "Usage:\n  agentskills <command> [flags]") {
		t.Fatalf("stdout did not contain usage:\n%s", stdout.String())
	}
	if stderr.Len() != 0 {
		t.Fatalf("stderr = %q, want empty", stderr.String())
	}
}

func TestRunUnknownCommandFailsWithUsage(t *testing.T) {
	var stdout, stderr bytes.Buffer

	code := run([]string{"nope"}, &stdout, &stderr)

	if code != 2 {
		t.Fatalf("exit code = %d, want 2", code)
	}
	if stdout.Len() != 0 {
		t.Fatalf("stdout = %q, want empty", stdout.String())
	}
	if !strings.Contains(stderr.String(), "unknown command: \"nope\"") {
		t.Fatalf("stderr did not contain unknown-command error:\n%s", stderr.String())
	}
	if !strings.Contains(stderr.String(), "Usage:\n  agentskills <command> [flags]") {
		t.Fatalf("stderr did not contain usage:\n%s", stderr.String())
	}
}
