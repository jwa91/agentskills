# Installation

agentskills publishes tagged GitHub Releases as the release source of truth.
Homebrew and direct downloads consume those release artifacts. `go install`
builds from the same module tag.

## Homebrew

```sh
brew install --cask jwa91/tap/agentskills
agentskills version
```

Update:

```sh
brew update
brew upgrade --cask agentskills
```

Uninstall:

```sh
brew uninstall --cask agentskills
```

## Direct Download

Download the archive for your platform from the [latest release](https://github.com/jwa91/agentskills/releases/latest). Asset names use this shape:

- `agentskills_<version>_darwin_arm64.tar.gz`
- `agentskills_<version>_darwin_amd64.tar.gz`
- `agentskills_<version>_linux_arm64.tar.gz`
- `agentskills_<version>_linux_amd64.tar.gz`

Verify and extract:

```sh
version=0.1.3
asset=agentskills_${version}_linux_amd64.tar.gz
curl -fsSLO "https://github.com/jwa91/agentskills/releases/download/v${version}/${asset}"
curl -fsSLO "https://github.com/jwa91/agentskills/releases/download/v${version}/checksums.txt"
grep "  $asset$" checksums.txt > "$asset.sha256"
shasum -a 256 -c "$asset.sha256"
tar -xzf "$asset"
./agentskills version
```

On Linux, use `sha256sum -c "$asset.sha256"` if `shasum` is not installed.

## Go

```sh
go install github.com/jwa91/agentskills/tools/agentskills@latest
agentskills version
```

For a pinned install:

```sh
go install github.com/jwa91/agentskills/tools/agentskills@v0.1.3
```

The Go install path builds from the module tag instead of downloading the
GitHub Release archive, so commit/date metadata may be less complete than
Homebrew or direct-release installs.

## Source Build

For alignment work that must use untagged changes, build from a checkout:

```sh
git clone https://github.com/jwa91/agentskills.git
cd agentskills
make build
./bin/agentskills version
```
