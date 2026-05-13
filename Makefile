.PHONY: build install test lint vet check clean tidy

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
