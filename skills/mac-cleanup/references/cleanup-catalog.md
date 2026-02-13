# Cleanup Catalog

Exhaustive reference for each cleanup category. Consult this when presenting options or executing cleanup commands.

Risk levels: **safe** (always reclaimable, rebuilds automatically), **moderate** (reclaimable but may need re-download or rebuild), **high** (data loss possible if wrong item chosen).

---

## Package Manager Caches

### Homebrew

- **Detection:** `which brew`
- **Cache location:** `$(brew --cache)` (typically `~/Library/Caches/Homebrew`)
- **Size check:** `du -sh $(brew --cache)`
- **Dry run:** `brew cleanup --dry-run -s`
- **Cleanup:** `brew cleanup -s`
- **Risk:** safe
- **Typical savings:** 1-10 GB
- **Notes:** `-s` also removes downloads for latest versions. Old formula/cask versions are pruned.

### npm

- **Detection:** `which npm`
- **Cache location:** `~/.npm`
- **Size check:** `du -sh ~/.npm`
- **Cleanup:** `npm cache clean --force`
- **Size check:** `du -sh ~/.npm` (note: `npm cache verify` also works but performs GC as a side effect)
- **Risk:** safe
- **Typical savings:** 200 MB - 2 GB

### pnpm

- **Detection:** `which pnpm`
- **Cache/store location:** `~/Library/pnpm/store` or `$(pnpm store path)`
- **Size check:** `du -sh $(pnpm store path)`
- **Cleanup:** `pnpm store prune`
- **Risk:** safe
- **Typical savings:** 500 MB - 5 GB
- **Notes:** Only removes unreferenced packages. Running projects are unaffected.

### yarn

- **Detection:** `which yarn`
- **Cache location:** `$(yarn cache dir)`
- **Size check:** `du -sh $(yarn cache dir)`
- **Cleanup:** `yarn cache clean`
- **Risk:** safe
- **Typical savings:** 200 MB - 3 GB

### bun

- **Detection:** `which bun`
- **Cache location:** `~/.bun/install/cache`
- **Size check:** `du -sh ~/.bun/install/cache`
- **Cleanup:** `bun pm cache rm`
- **Risk:** safe
- **Typical savings:** 100 MB - 2 GB

### uv

- **Detection:** `which uv`
- **Cache location:** `$(uv cache dir)`
- **Size check:** `du -sh $(uv cache dir)`
- **Cleanup:** `uv cache clean`
- **Risk:** safe
- **Typical savings:** 200 MB - 3 GB

### pip

- **Detection:** `which pip3` or `which pip`
- **Cache location:** `~/Library/Caches/pip`
- **Size check:** `du -sh ~/Library/Caches/pip`
- **Cleanup:** `pip cache purge`
- **Risk:** safe
- **Typical savings:** 100 MB - 1 GB

### cargo (Rust)

- **Detection:** `which cargo`
- **Cache location:** `~/.cargo/registry/cache`, `~/.cargo/registry/src`
- **Size check:** `du -sh ~/.cargo/registry`
- **Cleanup:** `cargo cache --autoclean` (requires `cargo-cache`), or manually `rm -rf ~/.cargo/registry/cache/* ~/.cargo/registry/src/*`
- **Risk:** safe (registry re-downloads on next build)
- **Typical savings:** 500 MB - 5 GB

### go

- **Detection:** `which go`
- **Cache location:** `$(go env GOMODCACHE)`, `$(go env GOCACHE)`
- **Cleanup:** `go clean -cache -modcache`
- **Risk:** safe
- **Typical savings:** 200 MB - 3 GB

### pyenv

- **Detection:** `which pyenv`
- **Cache location:** `~/.pyenv/cache`
- **Size check:** `du -sh ~/.pyenv/cache`
- **Cleanup:** `rm -rf ~/.pyenv/cache/*`
- **Risk:** safe (source tarballs only)
- **Typical savings:** 50-500 MB
- **Notes:** Installed Python versions live in `~/.pyenv/versions/` — only remove those the user explicitly wants gone.

---

## Developer Tool Caches

### Puppeteer

- **Detection:** `~/.cache/puppeteer`
- **Cleanup:** `rm -rf ~/.cache/puppeteer`
- **Risk:** safe (re-downloads on next puppeteer use)
- **Typical savings:** 500 MB - 2 GB

### pre-commit

- **Detection:** `~/.cache/pre-commit`
- **Cleanup:** `rm -rf ~/.cache/pre-commit`
- **Risk:** safe (re-clones on next pre-commit run)
- **Typical savings:** 50-200 MB

### ML/AI Model Caches

- **Detection:** `~/.cache/huggingface`, `~/.ollama/models`
- **Size check:** `du -sh ~/.cache/huggingface ~/.ollama/models 2>/dev/null`
- **Cleanup:** selectively delete unused models (list first)
- **Risk:** medium (re-download can be slow/large; ask before removing)
- **Typical savings:** 10-50+ GB

---

## System Caches & Logs

### ~/Library/Caches

- **Description:** Per-application caches (browser data, IDE indexes, etc.)
- **Size check:** `du -sh ~/Library/Caches`
- **Breakdown:** `du -sh ~/Library/Caches/*/ | sort -rh | head -15`
- **Risk:** moderate — apps rebuild caches, but some (e.g., Xcode derived data) take time
- **Safe to delete:** Most subdirectories. Apps will recreate them.
- **Caution:** Don't bulk-delete the entire folder. Review the breakdown and let the user choose which subdirectories to remove.
- **Common large entries:**
  - `com.apple.DeveloperTools` (Xcode)
  - `com.spotify.client`
  - `com.brave.Browser` / `com.google.Chrome`
  - `com.microsoft.VSCode`
  - `JetBrains` IDEs

### ~/Library/Logs

- **Description:** Application log files.
- **Size check:** `du -sh ~/Library/Logs`
- **Cleanup:** `rm -rf ~/Library/Logs/*`
- **Risk:** safe — logs are informational only
- **Typical savings:** 100 MB - 1 GB

### ~/.cache

- **Description:** XDG-style user cache (pip, uv, Hugging Face models, etc.)
- **Size check:** `du -sh ~/.cache`
- **Breakdown:** `du -sh ~/.cache/*/ | sort -rh | head -10`
- **Risk:** moderate — some caches (Hugging Face models) are large re-downloads
- **Notes:** Review breakdown before clearing. Tool-specific caches (pip, uv) are safe. ML model caches may be expensive to re-download.

---

## Dev Artifacts

### node_modules

- **Detection:** Presence of `node_modules/` in project directories
- **Staleness check:** mtime of files within
- **Cleanup:** `rm -rf <project>/node_modules`
- **Risk:** safe — `npm install` / `pnpm install` rebuilds from lockfile
- **Typical savings:** 100 MB - 1 GB per project
- **Notes:** Default stale threshold is 90 days since last modification.

### .venv / venv

- **Detection:** Presence of `.venv/` or `venv/` in project directories
- **Cleanup:** `rm -rf <project>/.venv`
- **Risk:** safe — recreatable from requirements/lockfile
- **Typical savings:** 50-500 MB per project

### .next (Next.js)

- **Detection:** `.next/` directory in project
- **Cleanup:** `rm -rf <project>/.next`
- **Risk:** safe — rebuild with `next build`
- **Typical savings:** 50-500 MB per project

### dist / build / target

- **Detection:** Build output directories
- **Cleanup:** `rm -rf <project>/dist` (or `build`, `target`)
- **Risk:** safe — rebuild from source
- **Typical savings:** 10-500 MB per project

### __pycache__ / .pytest_cache / .mypy_cache / .ruff_cache

- **Detection:** Python bytecode and tool caches
- **Cleanup:** `find <dev-dir> -type d -name __pycache__ -exec rm -rf {} +`
- **Risk:** safe — regenerated automatically
- **Typical savings:** 1-50 MB total

### Merged git branches

- **Detection:** `git branch --merged main | grep -v main` (per repo)
- **Cleanup:** `git branch --merged main | grep -v main | xargs git branch -d`
- **Risk:** safe — merged branches are fully integrated
- **Notes:** Only deletes local branches that have been merged into main/master.

---

## Docker

- **Detection:** `which docker` + `docker info` (check daemon is running)
- **Size check:** `docker system df`
- **Detailed:** `docker system df -v`
- **Conservative cleanup:** `docker system prune -f` (removes stopped containers, dangling images, unused networks)
- **Aggressive cleanup:** `docker system prune -a -f` (also removes all unused images, not just dangling)
- **Volume cleanup:** `docker volume prune -f` (removes unused volumes — **high risk**, may contain data)
- **Risk:**
  - `docker system prune -f`: moderate
  - `docker system prune -a -f`: moderate (re-pull images next time)
  - `docker volume prune -f`: **high** (potential data loss)
- **Typical savings:** 2-30 GB
- **Notes:** Always check if Docker daemon is running first. Show `docker system df` output and let user decide aggressiveness. Never prune volumes without explicit confirmation.

---

## Applications

### Detecting unused apps

- List installed casks: `brew list --cask`
- List all apps: `ls /Applications/`
- Ask user which apps they no longer use

### Uninstalling apps

- **Homebrew cask apps:** `brew uninstall --cask <name>`
- **Manual/App Store apps:** Use Finder via osascript:
  ```
  osascript -e 'tell application "Finder" to delete POSIX file "/Applications/AppName.app"'
  ```
- **NEVER** use `rm -rf /Applications/...` — use Finder to ensure proper Trash behavior
- **Quit the app first** before uninstalling

### Post-uninstall cleanup locations

After removing an `.app` bundle, check these 9 locations for leftover support files:

| Location | Contains |
|----------|----------|
| `~/Library/Application Support/<AppName>` | App data and configs |
| `~/Library/Caches/<bundleid>` | Cached data |
| `~/Library/Preferences/<bundleid>.plist` | Preference files |
| `~/Library/HTTPStorages/<bundleid>` | HTTP storage data |
| `~/Library/Logs/<AppName>` | Log files |
| `~/Library/Containers/<bundleid>` | Sandboxed app data |
| `~/Library/Group Containers/<group.bundleid>` | Shared group data |
| `~/Library/Saved Application State/<bundleid>.savedState` | Window state |
| `~/Library/WebKit/<bundleid>` | WebKit data |

- **Risk:** moderate — make sure the app is truly uninstalled before cleaning these
- **Notes:** Bundle IDs follow reverse-DNS convention (e.g., `com.brave.Browser`). Use `mdls -name kMDItemCFBundleIdentifier /Applications/AppName.app` to find the bundle ID before uninstalling.

---

## Trash

- **Path:** `~/.Trash`
- **Size check:** `du -sh ~/.Trash`
- **Cleanup:** `rm -rf ~/.Trash/*`
- **Risk:** moderate — user may want to recover recently trashed items
- **Notes:** Show size and ask before emptying. macOS Trash is the safety net for deleted files.

---

## Downloads

- **Path:** `~/Downloads`
- **Size check:** `du -sh ~/Downloads`
- **Cleanup:** `rm -rf ~/Downloads/*` (or selective deletion)
- **Risk:** high — may contain files the user still needs
- **Notes:** Never bulk-delete without showing contents and getting approval. Offer to show the largest files first. Consider sorting by age.
