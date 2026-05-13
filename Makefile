.PHONY: build install test lint clean tidy

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

tidy:
	go mod tidy

clean:
	rm -rf bin dist
