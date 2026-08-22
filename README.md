# macOS dotfiles

Public, reproducible configuration for the dedicated `agents` macOS user. The
repository uses mise's native bootstrap/dotfiles support and keeps credentials,
Hermes state, sessions, caches, and application data outside Git.

Live application is intentionally deferred. Review
[`docs/live-apply-proposal.md`](docs/live-apply-proposal.md) before replacing any
existing file.

## Ownership boundaries

- `mise.toml` manages user-owned development tools and three public-safe
  dotfiles.
- `Brewfile` records shared Homebrew formulae and casks. Homebrew is owned by
  the administrator account; Hermes may inspect and propose changes but does
  not install, upgrade, or remove Homebrew packages.
- Hermes owns `~/.hermes/node`, its Python runtime, and its virtual environment.
  This repository does not replace or update them independently.
- Codex CLI stays on OpenAI's official npm-global stable route. It is not
  version-pinned or automatically updated by `mise bootstrap`.
- Authentication remains manual. No token, OAuth state, SSH material, shell
  history, Hermes profile, memory, or session belongs here.

## Declared state

- mise tool: `pnpm = "11.22.0"`, resolved in `mise.lock`
- dotfiles: `~/.zshrc`, `~/.gitconfig`, and
  `~/.config/mise/config.toml`
- Homebrew: 11 direct formulae and 3 casks in `Brewfile`

Observed but intentionally undeclared inventory is never deleted or pruned:

- inactive Python 3.11.15
- old pnpm 10.30.3 and 11.18.0
- transitive Homebrew formulae `gmp`, `oniguruma`, and `pcre2`

## First-machine order

1. Install Homebrew and mise through their official stable routes.
2. Clone this repository to `~/Repos/dotfiles`.
3. As the administrator, inspect and apply shared packages:

   ```sh
   brew bundle check --file ~/Repos/dotfiles/Brewfile
   brew bundle --file ~/Repos/dotfiles/Brewfile
   ```

   `brew bundle` installs missing declarations; upgrades and removals remain
   separate, explicit administrator actions.

4. Install Hermes Agent through its official stable installer. Hermes manages
   its own Node/Python runtime and configuration migrations.
5. As `agents`, inspect the repository-owned setup:

   ```sh
   cd ~/Repos/dotfiles
   mise trust
   mise fmt --check
   mise tasks validate
   mise bootstrap status
   mise bootstrap dotfiles status
   mise bootstrap --dry-run
   ```

6. Back up and review conflicting live files before any real dotfile apply.
   Never add `--force`, `--force-dotfiles`, update, upgrade, or prune flags to
   the first application.
7. Install the current stable Codex CLI explicitly after Hermes supplies
   Node/npm:

   ```sh
   npm install --global @openai/codex@latest
   codex --version
   ```

8. Authenticate GitHub, Hermes, Codex, Discord, and MCP services manually.

## Read-only update checks

User-owned tools can be checked through their official managers. Homebrew's
package catalog can be refreshed without updating Homebrew itself or changing
installed packages:

```sh
HOMEBREW_NO_AUTO_UPDATE=1 \
HOMEBREW_FORCE_API_AUTO_UPDATE=1 \
brew outdated --json=v2
```

Hermes may report Homebrew candidates and exact administrator commands, but it
does not execute Homebrew mutations.

## Rollback

Before an approved apply, save the current `~/.zshrc`, `~/.gitconfig`, and
`~/.config/mise/config.toml`. To roll back, remove only a repository-owned
symlink that still points to this checkout, then restore the saved regular
file. Homebrew, Codex, Hermes, uv, and authentication state are not dotfile
rollback targets.

## License

MIT
