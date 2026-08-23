# Apple Silicon Mac 環境セットアップ

このリポジトリは、Hermes専用Macで使う公開設定を管理します。まず人間が、管理者アカウントと標準アカウントを用意し、必要なアプリをインストールします。そこまで終わったら、AIにこのリポジトリと `AGENTS.md` を読ませて、設定の適用やHermes構成を案内させます。

## 最低限の完了状態

次の状態まで人間が準備します。

- Apple Silicon Macに管理者アカウントがある
- `agents` という標準アカウントがある
- 管理者がHomebrewと共有アプリをインストールしている
- `agents` がmise、Hermes Agent、Codex CLIをインストールしている
- 管理者用cloneが `/Users/estrilda/Repos/dotfiles` にある
- このリポジトリが `/Users/agents/Repos/dotfiles` にある
- `users/agents` のmise設定とdotfilesが適用されている

Hermesのプロバイダー、`default` / `coder` プロファイル、Discord、Gateway、cron、各種認証は、その後AIと確認しながら設定します。

## 1. アカウントを用意する

macOSの初期設定で管理者アカウントを作ります。次に、管理者アカウントから **システム設定 → ユーザとグループ** を開き、次の標準アカウントを追加します。

- アカウント名：`agents`
- 種類：標準ユーザー

Hermesと開発ツールは `agents` で実行します。Homebrewと共有アプリの変更は管理者が行います。

## 2. 管理者がHomebrewをインストールする

管理者アカウントで、公式installerからHomebrewをインストールします。

```sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
eval "$(/opt/homebrew/bin/brew shellenv)"
```

Homebrewは `/opt/homebrew` に置き、管理者アカウントが所有します。

管理者専用のcloneも作ります。このcloneはHomebrew変更前のレビューにだけ使い、Hermesから操作しません。

```sh
mkdir -p /Users/estrilda/Repos
git clone https://github.com/big-mon/dotfiles.git /Users/estrilda/Repos/dotfiles
cd /Users/estrilda/Repos/dotfiles
git status --short --branch
git show HEAD:hosts/hermes-macos/Brewfile
```

## 3. 管理者が共有アプリをインストールする

そのまま管理者アカウントで、管理者専用cloneを更新します。pull前のcommitを保存し、取得した全commitに含まれるBrewfile差分と現在のBrewfile全体を確認してから適用します。

```sh
cd /Users/estrilda/Repos/dotfiles
git status --short --branch
previous=$(git rev-parse HEAD)
git pull --ff-only
git diff "$previous"..HEAD -- hosts/hermes-macos/Brewfile
git show HEAD:hosts/hermes-macos/Brewfile

/opt/homebrew/bin/brew bundle check --file hosts/hermes-macos/Brewfile
/opt/homebrew/bin/brew bundle --file hosts/hermes-macos/Brewfile
```

`git status` がcleanでない場合や、Brewfileの変更意図を説明できない場合は適用しません。管理者用コマンドから `/Users/agents/Repos/dotfiles` を参照しないでください。

主に次のアプリとCLIが入ります。

- GUI：Ghostty、Obsidian、Zed
- Git/GitHub：GitHub CLI、Git LFS
- zsh補助：zsh-autosuggestions、zsh-syntax-highlighting

正確な直接依存は `hosts/hermes-macos/Brewfile` を基準にします。

## 4. `agents` がmiseを入れてリポジトリを取得する

ここで初めて `agents` へサインインし、miseをユーザー領域へインストールします。

```sh
curl https://mise.run | sh
export PATH="$HOME/.local/bin:$PATH"
```

続いて公開リポジトリを取得します。

```sh
mkdir -p ~/Repos
git clone https://github.com/big-mon/dotfiles.git ~/Repos/dotfiles
```

## 5. `agents` がユーザー設定を適用する

続けて `agents` で適用内容を確認します。

```sh
cd ~/Repos/dotfiles/users/agents
mise trust
mise fmt --check
mise bootstrap dotfiles status
mise bootstrap --dry-run
```

既存ファイルとの競合が表示された場合は、その場で上書きせず、AIにバックアップ方法を確認してください。確認後に適用します。

```sh
mise bootstrap --yes
mise trust ~/.config/mise/config.toml
mise bootstrap status --missing
```

最後のコマンドが成功し、dotfileが `applied`、ツールが `installed` なら完了です。miseはユーザー用Python・uv・pnpmに加え、検索・データ処理・シェル検証用CLIを管理します。新しいシェル設定を読むため、ログインシェルを開き直します。

```sh
exec zsh -l
```

## 6. `agents` がHermesとCodexをインストールする

Hermes Agentは公式のユーザー向けinstallerで入れます。

```sh
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
hermes --version
```

Hermes installerは`~/.hermes`内の専用uv、Python、Node.jsを管理します。miseが管理するユーザー用ツールとは分離したままにします。Hermes付属のnpmからCodex CLIを入れます。

```sh
npm install --global @openai/codex@latest
codex --version
```

## 7. AIへ引き継ぐ

ここまで終わったら、`agents` でこのリポジトリを開き、AIへ次のように依頼します。

> `/Users/agents/Repos/dotfiles` の `AGENTS.md` と現在の環境を確認し、未完了のセットアップを順番に説明して。管理者操作は管理者用コマンドとして分けて提示して。

AIは `AGENTS.md` を基準に、認証、Hermesプロファイル、Gateway、Discord、cronなどの残作業を案内します。

## ライセンス

MIT
