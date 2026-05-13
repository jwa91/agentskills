.PHONY: build install test lint vet check clean tidy release

BIN_DIR ?= $(HOME)/.local/bin
PKG     := ./tools/agentskills
BIN     := agentskills

build:
	go build -o bin/$(BIN) $(PKG)

install:
	go install $(PKG)

# Run the Go test suite with coverage reporting for the internal/ packages.
test:
	go test -cover ./...

# Optional: golangci-lint if you've installed it. Falls back to `go vet`.
lint:
	@if command -v golangci-lint >/dev/null 2>&1; then \
		golangci-lint run ./...; \
	else \
		echo "golangci-lint not installed; running go vet instead"; \
		go vet ./...; \
	fi

vet:
	go vet ./...

# Local verification suite mirrored by .github/workflows/ci.yml. Trimmed
# vs. prehandover: no staticcheck/govulncheck because agentskills has zero
# third-party Go dependencies.
check: vet lint build test

tidy:
	go mod tidy

clean:
	rm -rf bin dist

# Local release. CI is workflow_dispatch-only until signing creds are in
# CI; until then every release runs locally. Requires 1Password signed
# in, the v$(VERSION) tag at HEAD, and a keychain profile named
# "notarytool" (xcrun notarytool store-credentials).
release:
	@test -n "$(VERSION)" || (echo "usage: make release VERSION=X.Y.Z" && exit 2)
	@op whoami >/dev/null || (echo "1Password not signed in: eval \$$(op signin)" && exit 1)
	@gh auth status >/dev/null 2>&1 || (echo "gh not authenticated: gh auth login" && exit 1)
	@xcrun notarytool history --keychain-profile notarytool >/dev/null 2>&1 || \
	  (echo "keychain profile 'notarytool' missing — see scripts/notarize-darwin.sh header"; exit 1)
	@existing=$$(git rev-parse -q --verify "v$(VERSION)^{commit}" 2>/dev/null); \
	head=$$(git rev-parse HEAD); \
	test -n "$$existing" && test "$$existing" = "$$head" || \
	  (echo "v$(VERSION) must exist and point at HEAD before release"; exit 3)
	# Build + codesign + archive + publish + commit Cask back to the tap.
	GITHUB_TOKEN="$$(gh auth token)" \
	  jwa-harden run -- goreleaser release --clean
	# Submit each codesigned darwin binary to notarytool.
	scripts/notarize-darwin.sh agentskills $(VERSION)
