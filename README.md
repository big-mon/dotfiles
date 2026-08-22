# macOS dotfiles

Public configuration for the dedicated `agents` macOS account. Credentials,
Hermes state, sessions, caches, and application data stay outside this
repository.

## Management boundaries

- `mise.toml` is the source of truth for user-owned tools and symlinked
  dotfiles.
- `Brewfile` declares shared packages. The administrator account reviews and
  applies Homebrew changes.
- Hermes manages its bundled runtimes and migrations. Codex CLI remains on its
  official npm-global stable installation route.
- Authentication is manual and external to this repository.

## Set up another machine

1. Install Homebrew and mise through their official stable routes, then clone
   this repository to `~/Repos/dotfiles`.
2. As the administrator, review and apply `Brewfile`:

   ```sh
   brew bundle check --file ~/Repos/dotfiles/Brewfile
   brew bundle --file ~/Repos/dotfiles/Brewfile
   ```

3. As `agents`, review mise's plan before applying it:

   ```sh
   cd ~/Repos/dotfiles
   mise trust
   mise fmt --check
   mise bootstrap status
   mise bootstrap --dry-run
   ```

   Back up any conflicting target first. Apply without force flags only after
   reviewing the dry run:

   ```sh
   mise bootstrap --yes
   mise bootstrap status
   ```

4. Install Hermes Agent and Codex CLI through their official stable routes,
   then authenticate services manually.

`~/.zprofile` exposes mise shims to login shells and their non-interactive child
processes. `~/.zshrc` keeps interactive mise activation. A launchd service
captures `PATH` when installed, so regenerate Hermes Gateway services from a
login shell after first applying the profile.

## Weekly snapshot

The weekly environment-update cron runs `scripts/publish-dotfiles` before its
read-only software update check. The helper validates the repository, rejects
common secret files and private-key material, and pushes a dated commit when
local dotfiles changed. A failed snapshot is reported without force operations
or package changes.

## Roll back

Remove a symlink only when it still points into this checkout, then restore the
file backed up during setup. Package, runtime, and authentication state are
outside dotfile rollback.

## License

MIT
