# Apple Silicon macOS environment

Public configuration for a dedicated Hermes machine. The design separates
system administration from day-to-day agent operation and keeps credentials,
Hermes state, sessions, and application data outside Git.

## Account model

### Administrator account

The administrator account is used only for macOS administration and shared
software. It owns Homebrew at `/opt/homebrew` and applies updates to the
`Brewfile`. Hermes does not run from this account.

Install Homebrew itself, then the direct packages declared in `Brewfile`:

| Group | Software | Purpose |
| --- | --- | --- |
| GUI applications | Ghostty, Obsidian, Zed | Terminal, notes, and editor available to the standard account |
| General CLI | `fd`, `jq`, `ripgrep`, `tree`, `yq` | Search and structured-data utilities |
| GitHub/Git | GitHub CLI (`gh`), Git LFS | Repository access and large-file support |
| Validation | ShellCheck, shfmt | Shell-script checks used by the dotfiles snapshot |
| Shell additions | zsh-autosuggestions, zsh-syntax-highlighting | Interactive zsh support |

`Brewfile` remains the authoritative package list; transitive Homebrew
dependencies are not documented separately.

### Standard account: `agents`

`agents` is a non-administrator account that owns repositories, agent tooling,
and user configuration.

| Software | Installation owner and route |
| --- | --- |
| mise | Per-user standalone installer; executable at `~/.local/bin/mise` |
| pnpm | Installed by mise from `mise.toml` and `mise.lock` |
| Hermes Agent | Official per-user installer under `~/.hermes` with launcher in `~/.local/bin` |
| uv, Python, Node.js, ripgrep, ffmpeg | Supplied or resolved by the Hermes installer; do not manage them as separate user installations |
| Codex CLI | Official npm-global package, installed with the Node/npm supplied by Hermes |
| GitHub CLI and GUI applications | Shared installations supplied by the administrator's Homebrew setup |

GitHub, Codex, model-provider, Discord, and other authentication is performed as
`agents`. Credential values and OAuth state are never stored in this repository.

## Build a new Mac

### 1. Create the accounts and install Homebrew

During macOS setup, create an administrator account. From that account, add a
separate **Standard** account named `agents` in **System Settings → Users &
Groups**.

Still in the administrator account, install Homebrew through its official
installer and load it into the current shell:

```sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
eval "$(/opt/homebrew/bin/brew shellenv)"
```

The Homebrew installation must remain owned by the administrator account.

### 2. Install mise and clone the repository as `agents`

Sign in as `agents` and install mise through its per-user installer:

```sh
curl https://mise.run | sh
export PATH="$HOME/.local/bin:$PATH"
```

Clone the public repository:

```sh
mkdir -p ~/Repos
git clone https://github.com/big-mon/dotfiles.git ~/Repos/dotfiles
cd ~/Repos/dotfiles
```

### 3. Apply shared packages as the administrator

Return to an administrator shell. Use the absolute path because `~` would refer
to the administrator account:

```sh
/opt/homebrew/bin/brew bundle check --file /Users/agents/Repos/dotfiles/Brewfile
/opt/homebrew/bin/brew bundle --file /Users/agents/Repos/dotfiles/Brewfile
```

This installs the shared command-line tools and GUI applications listed above.
Package upgrades and removals remain administrator actions.

### 4. Apply user tools and dotfiles as `agents`

Return to the `agents` shell and inspect mise's plan:

```sh
cd ~/Repos/dotfiles
mise trust
mise fmt --check
mise bootstrap dotfiles status
mise bootstrap --dry-run
```

If mise reports an existing-file conflict, move that target to a backup outside
the managed path and repeat the dry run. Apply only when the plan contains no
unreviewed replacement:

```sh
mise bootstrap --yes
mise trust ~/.config/mise/config.toml
mise bootstrap status --missing
```

The second trust applies to the newly linked user-level mise config. This step
is complete when the final command exits successfully and every declared
dotfile is `applied` and every declared tool is `installed`.

Start a fresh login shell so it reads the managed `.zprofile` and `.zshrc`:

```sh
exec zsh -l
```

### 5. Install Hermes and Codex as `agents`

Install Hermes through its official per-user installer, configure a working
provider, and run its static diagnostics:

```sh
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
hermes setup
hermes doctor
```

The Hermes installer manages its own Python and Node.js runtimes. Use that npm
to install Codex CLI:

```sh
npm install --global @openai/codex@latest
codex login
codex login status
gh auth login
gh auth status
```

### 6. Recreate non-secret Hermes structure

Keep `default` as the daily-assistant profile and create `coder` for software
development. Profile creation also creates the `coder` launcher:

```sh
hermes profile create coder
coder setup
hermes profile list
```

Configure and install the two messaging Gateways separately:

```sh
hermes gateway setup
hermes gateway install
coder gateway setup
coder gateway install
hermes gateway list
```

Provider and messaging setup writes credentials outside this repository. The
weekly environment-update cron belongs to `default`; it runs
`scripts/publish-dotfiles` before its read-only update check, committing changed
public dotfiles without copying credentials into Git.

## Roll back dotfiles

Remove a symlink only when it still points into this checkout, then restore the
file backed up during setup. Package, runtime, Hermes, and authentication state
are outside dotfile rollback.

## License

MIT
