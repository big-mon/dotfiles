# Live-apply proposal

This is a proposal only. No live dotfile, package, runtime, credential, or
application state has been changed.

## Proposed dotfile targets

| Live target | Repository source | Mode | Expected effect | Rollback |
| --- | --- | --- | --- | --- |
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

`dotfiles/zshrc` intentionally keeps:

```zsh
eval "$(mise activate zsh)"
```

in `.zshrc`, preserving activation for login and non-login interactive zsh
sessions. No `.zprofile` target is introduced.

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

Only after reviewing backups and approving the three target replacements:

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
