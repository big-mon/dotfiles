# Live-apply proposal

This is a proposal only. No live dotfile, package, runtime, credential, or
application state has been changed.

## Proposed dotfile targets

| Live target | Repository source | Mode | Expected effect | Rollback |
| --- | --- | --- | --- | --- |
| `~/.zprofile` | `dotfiles/zprofile` | whole-file symlink | Add mise shims to login-shell PATH so non-interactive child processes resolve current mise-managed tools without a version-specific install path. The target is currently absent. | Remove only the repository-owned symlink. |
| `~/.zshrc` | `dotfiles/zshrc` | whole-file symlink | Preserve the current PATH, file-descriptor limit, mise activation, Homebrew shell helpers, and editor settings. | Remove only the repository-owned symlink and restore the reviewed backup. |
| `~/.gitconfig` | `dotfiles/gitconfig` | whole-file symlink | Manage the public Git identity, Git LFS filters, and nonsecret `gh` credential-helper routing. | Remove only the repository-owned symlink and restore the reviewed backup. |
| `~/.config/mise/config.toml` | `dotfiles/mise/config.toml` | whole-file symlink | Preserve the current declared pnpm 11.22.0 tool. | Remove only the repository-owned symlink and restore the reviewed backup before the next mise invocation. |

mise must refuse existing regular-file conflicts unless they are handled
explicitly. The first apply must not use `--force` or `--force-dotfiles`.

## Exact Git identity

```gitconfig
[user]
    name = big-mon
    email = 26018409+big-mon@users.noreply.github.com
```

The repository stores no credential value. The `gh auth git-credential` helper
continues to read authentication from GitHub CLI's external credential store.

## Shell activation

`dotfiles/zprofile` adds the stable shim path:

```zsh
export PATH="$HOME/.local/share/mise/shims:$PATH"
```

`dotfiles/zshrc` separately keeps:

```zsh
eval "$(mise activate zsh)"
```

in `.zshrc`, preserving directory-aware activation for login and non-login
interactive zsh sessions. The two files have distinct roles: shims for
non-interactive children, full activation for interactive shells.

Hermes Gateway runs under launchd and does not source either file itself. Its
plist captures the invoking shell's PATH at service installation time. After
live application, regenerate the default and Coder Gateway services from a
separate login shell so their plists capture the shim directory. This service
operation is not authorized or executed by the repository-only change.

## Package boundaries

- `Brewfile` is the single declaration of shared Homebrew formulae and casks.
  It is inspected/applied by the administrator, not by Hermes or mise running
  as `agents`.
- `mise.toml` manages only user-owned mise tools and dotfiles.
- Codex CLI remains an explicit official npm-global stable install:

  ```sh
  npm install --global @openai/codex@latest
  ```

  It is not run automatically by `mise bootstrap`.
- Hermes, its managed Node/Python/venv, uv, credentials, and application state
  are outside this repository's apply surface.

## Proposed first application

Only after reviewing backups and approving the four target changes:

```sh
cd ~/Repos/dotfiles
mise trust
mise bootstrap --dry-run
# Back up and explicitly resolve the three regular-file conflicts.
mise bootstrap --yes
mise bootstrap status
```

The exact backup and conflict-resolution commands must be shown before they are
run. No package update, cleanup, pruning, Homebrew mutation, authentication, or
force flag is authorized by this proposal.
