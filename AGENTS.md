# AGENTS.md

## Purpose

Use this repository to complete and maintain a dedicated Apple Silicon Mac for Hermes Agent. `README.md` is the human bootstrap guide. This file begins where that guide hands control to an agent.

Do not repeat completed installation blindly. Inspect the live machine, identify the missing state, and act only within the ownership boundaries below.

## Expected entry state

Assume the human has completed the minimum steps in `README.md`:

- macOS has an administrator account and a non-administrator account named `agents`.
- The administrator owns Homebrew at `/opt/homebrew`.
- This repository exists at `/Users/agents/Repos/dotfiles`.
- Shared applications come from `hosts/hermes-macos/Brewfile`.
- `agents` has mise, Hermes Agent, and Codex CLI installed.
- mise has applied the configuration under `users/agents`.
- Credentials, OAuth state, Hermes profiles, sessions, memories, and application data remain outside Git.

Verify these assumptions before relying on them. If a prerequisite is missing, explain the corresponding human step from `README.md` rather than improvising another installation route.

## Sources of truth

- `hosts/hermes-macos/Brewfile`: direct shared Homebrew formulae and casks.
- `users/agents/mise.toml` and `mise.lock`: user-owned tools and managed dotfiles.
- `users/agents/dotfiles/`: public files symlinked into the `agents` home directory.
- `scripts/publish-dotfiles`: validated weekly snapshot helper.
- `tests/`: behavior checks for the snapshot helper.
- `README.md`: human account and software bootstrap.

Read these sources instead of copying current versions, package counts, or target lists into another document.

## Ownership boundaries

### Administrator

The administrator owns all Homebrew mutations under `/opt/homebrew`. From the `agents` account, inspect Homebrew and provide exact administrator commands, but do not install, upgrade, remove, prune, or repair Homebrew packages.

### `agents`

- mise owns pnpm and the symlinks declared in `users/agents/mise.toml`.
- Hermes owns its uv, Python, Node.js, virtual environment, and migrations under `~/.hermes`.
- Codex CLI follows the official npm-global stable route using Hermes-supplied npm.
- GitHub CLI is shared through Homebrew; its authentication belongs to `agents`.

Keep these managers separate. Do not move Hermes runtimes into mise, add Codex to mise, or let Hermes mutate Homebrew.

## Agent procedure

### 1. Establish the baseline

Inspect the platform, current account, `/opt/homebrew` ownership, required commands, mise status, live symlink targets, Hermes profiles, and Gateway status. The baseline is complete when every expected component is accounted for as present, missing, or intentionally external.

### 2. Reconcile repository-managed state

Check the administrator bundle without upgrading it:

```sh
HOMEBREW_NO_AUTO_UPDATE=1 /opt/homebrew/bin/brew bundle check --no-upgrade --file /Users/agents/Repos/dotfiles/hosts/hermes-macos/Brewfile
```

Check the standard-account configuration from its own directory:

```sh
cd /Users/agents/Repos/dotfiles/users/agents
mise fmt --check
mise bootstrap dotfiles status
mise bootstrap --dry-run
```

For each existing-file conflict, show the exact target and proposed backup destination before moving anything. Wait for human approval of filesystem moves. Apply without force flags. Completion requires every declared dotfile to be `applied`, every declared tool to be `installed`, and every live symlink to resolve into `users/agents/dotfiles`.

### 3. Reconcile non-secret Hermes structure

The intended profile split is:

- `default`: daily assistant and owner of the weekly environment-update cron.
- `coder`: software-development work.

Configure provider credentials and messaging interactively, outside Git. A Gateway is ready only after its profile completes a normal CLI chat and `hermes gateway list` reports the service running. Never print or write credential values into repository files.

### 4. Preserve maintenance behavior

Live dotfiles are symlinks into this checkout. The `default` profile's weekly environment-update cron runs `scripts/publish-dotfiles` before its read-only update check.

The snapshot helper must remain fail-closed: validate the `agents` mise configuration, run tests, reject likely secret material, show the staged changes, then commit and push. It does not pull, rebase, reset, force-push, rewrite history, or update packages.

The external monitor at `~/.hermes/scripts/environment_update_snapshot.py` must continue to reference:

- `/Users/agents/Repos/dotfiles/hosts/hermes-macos/Brewfile`
- `/Users/agents/Repos/dotfiles/users/agents`

A layout change is incomplete until the monitor runs successfully against the new paths.

## Verification

After repository changes, run:

```sh
cd /Users/agents/Repos/dotfiles
python3 -m unittest discover -s tests -v
shellcheck scripts/publish-dotfiles
shfmt -d scripts/publish-dotfiles
git diff --check

MISE_TRUSTED_CONFIG_PATHS=/Users/agents/Repos/dotfiles/users/agents \
  mise -C /Users/agents/Repos/dotfiles/users/agents fmt --check
MISE_TRUSTED_CONFIG_PATHS=/Users/agents/Repos/dotfiles/users/agents \
  mise -C /Users/agents/Repos/dotfiles/users/agents tasks validate
MISE_TRUSTED_CONFIG_PATHS=/Users/agents/Repos/dotfiles/users/agents \
  mise -C /Users/agents/Repos/dotfiles/users/agents bootstrap status --missing
```

Also verify Homebrew bundle satisfaction, live symlink targets, and a monitor snapshot with no errors. Work is complete only when all affected automation paths have been exercised and the repository contains no credential material.
