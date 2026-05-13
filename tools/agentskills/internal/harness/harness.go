// Package harness owns the embedded harness-adapter table and the
// symlink logic that links non-native harness skill folders into the
// canonical .agents/skills directory.
//
// The adapter table is sourced from src/agentskills/harness_adapters.json
// at build time via //go:embed, so the binary and Python CLI cannot drift.
package harness

import (
	_ "embed"
	"encoding/json"
	"fmt"
	"sort"
)

//go:embed harness_adapters.json
var embeddedConfigBytes []byte

// Adapter describes how one harness expects to find skill content.
type Adapter struct {
	RelativeLinkPath string `json:"relative_link_path"`
	Description      string `json:"description"`
}

// Config is the parsed shape of harness_adapters.json.
type Config struct {
	CanonicalSkillsDir string             `json:"canonical_skills_dir"`
	Adapters           map[string]Adapter `json:"adapters"`
}

// LoadEmbedded returns the embedded harness adapter table.
func LoadEmbedded() (*Config, error) {
	return parse(embeddedConfigBytes)
}

// LoadFromBytes parses an external adapter config (used when the user
// passes --config to override the embedded table).
func LoadFromBytes(data []byte) (*Config, error) { return parse(data) }

func parse(data []byte) (*Config, error) {
	var c Config
	if err := json.Unmarshal(data, &c); err != nil {
		return nil, fmt.Errorf("parse harness config: %w", err)
	}
	if c.CanonicalSkillsDir == "" || c.Adapters == nil {
		return nil, fmt.Errorf("config must contain canonical_skills_dir and adapters")
	}
	return &c, nil
}

// Names returns the adapter names in sorted order.
func (c *Config) Names() []string {
	names := make([]string, 0, len(c.Adapters))
	for n := range c.Adapters {
		names = append(names, n)
	}
	sort.Strings(names)
	return names
}

// Resolve returns the adapter for the given name.
func (c *Config) Resolve(name string) (Adapter, bool) {
	a, ok := c.Adapters[name]
	return a, ok
}
