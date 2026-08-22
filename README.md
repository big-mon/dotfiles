# Apple Silicon macOS dotfiles

Public configuration for the dedicated `agents` macOS account. This repository
reproduces shared packages, user-owned tools, and symlinked dotfiles. It does not
restore credentials, Hermes profiles, gateways, sessions, or application data.

## Management boundaries

- `mise.toml` is the source of truth for user-owned tools and symlinked
  dotfiles.
- `Brewfile` declares shared packages. The administrator account reviews and
  applies Homebrew changes.
- Hermes manages its bundled runtimes and migrations. Codex CLI remains on its
  official npm-global stable installation route.
- Authentication is manual and external to this repository.

## Apply on another Mac

Prerequisites are an Apple Silicon Mac, a standard account named `agents`,
administrator access, Homebrew installed under `/opt/homebrew`, and mise
installed for `agents`.

1. As `agents`, clone the public repository:

   ```sh
   mkdir -p ~/Repos
   git clone https://github.com/big-mon/dotfiles.git ~/Repos/dotfiles
   cd ~/Repos/dotfiles
   ```

2. From an administrator shell, review and apply the shared packages. Use the
   absolute path because `~` would refer to the administrator account:

   ```sh
   brew bundle check --file /Users/agents/Repos/dotfiles/Brewfile
   brew bundle --file /Users/agents/Repos/dotfiles/Brewfile
   ```

3. Back in the `agents` shell, inspect mise's plan:

   ```sh
   cd ~/Repos/dotfiles
   mise trust
   mise fmt --check
   mise bootstrap dotfiles status
   mise bootstrap --dry-run
   ```

   If mise reports an existing-file conflict, move that target to a backup
   outside the managed path and repeat the dry run. Apply only when the plan
   contains no unreviewed replacement:

   ```sh
   mise bootstrap --yes
   mise trust ~/.config/mise/config.toml
   mise bootstrap status --missing
   ```

   The second trust applies to the newly linked user-level mise config. Setup is
   complete when the final command exits successfully and every declared
   dotfile is `applied` and every declared tool is `installed`.

4. Start a fresh login shell so it reads the new `.zprofile` and `.zshrc`:

   ```sh
   exec zsh -l
   ```

5. Install Hermes Agent, then configure it and verify the installation:

   ```sh
   curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
   hermes setup
   hermes doctor
   ```

6. Install and authenticate Codex CLI through its official npm package, then
   authenticate GitHub CLI:

   ```sh
   npm install --global @openai/codex@latest
   codex login
   codex login status
   gh auth login
   gh auth status
   ```

Hermes profiles, gateways, messaging channels, and other credentials are
configured separately; this repository deliberately does not reproduce them.

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
