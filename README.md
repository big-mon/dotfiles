# Apple Silicon Mac 環境セットアップ

このリポジトリは、Hermes専用Macで使う公開設定を管理します。まず人間が、管理者アカウントと標準アカウントを用意し、必要なアプリをインストールします。そこまで終わったら、AIにこのリポジトリと `AGENTS.md` を読ませて、設定の適用やHermes構成を案内させます。

パスワード、APIキー、OAuth情報などの秘密情報は、このリポジトリへ保存しません。

## 最低限の完了状態

次の状態まで人間が準備します。

- Apple Silicon Macに管理者アカウントがある
- `agents` という標準アカウントがある
- 管理者がHomebrewと共有アプリをインストールしている
- `agents` がmise、Hermes Agent、Codex CLIをインストールしている
- このリポジトリが `/Users/agents/Repos/dotfiles` にある
- `accounts/agents` のmise設定とdotfilesが適用されている

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

## 3. `agents` がmiseを入れてリポジトリを取得する

`agents` へサインインし、miseをユーザー領域へインストールします。

```sh
curl https://mise.run | sh
export PATH="$HOME/.local/bin:$PATH"
```

続いて公開リポジトリを取得します。

```sh
mkdir -p ~/Repos
git clone https://github.com/big-mon/dotfiles.git ~/Repos/dotfiles
```

## 4. 管理者が共有アプリをインストールする

管理者アカウントへ戻り、`accounts/admin/Brewfile` を適用します。

```sh
/opt/homebrew/bin/brew bundle check --file /Users/agents/Repos/dotfiles/accounts/admin/Brewfile
/opt/homebrew/bin/brew bundle --file /Users/agents/Repos/dotfiles/accounts/admin/Brewfile
```

主に次のアプリとCLIが入ります。

- GUI：Ghostty、Obsidian、Zed
- Git/GitHub：GitHub CLI、Git LFS
- 検索・データ処理：fd、ripgrep、jq、yq、tree
- シェル検証：ShellCheck、shfmt
- zsh補助：zsh-autosuggestions、zsh-syntax-highlighting

正確な直接依存は `accounts/admin/Brewfile` を基準にします。

## 5. `agents` がユーザー設定を適用する

`agents` へ戻り、適用内容を先に確認します。

```sh
cd ~/Repos/dotfiles/accounts/agents
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

最後のコマンドが成功し、dotfileが `applied`、ツールが `installed` なら完了です。新しいシェル設定を読むため、ログインシェルを開き直します。

```sh
exec zsh -l
```

## 6. `agents` がHermesとCodexをインストールする

Hermes Agentは公式のユーザー向けinstallerで入れます。

```sh
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
hermes --version
```

Hermes installerがユーザー領域のuv、Python、Node.jsなどを管理するため、これらを別経路で追加する必要はありません。Hermes付属のnpmからCodex CLIを入れます。

```sh
npm install --global @openai/codex@latest
codex --version
```

## 7. AIへ引き継ぐ

ここまで終わったら、`agents` でこのリポジトリを開き、AIへ次のように依頼します。

> `/Users/agents/Repos/dotfiles` の `AGENTS.md` と現在の環境を確認し、未完了のセットアップを順番に説明して。秘密情報はGitへ保存せず、管理者操作は管理者用コマンドとして分けて提示して。

AIは `AGENTS.md` を基準に、認証、Hermesプロファイル、Gateway、Discord、cronなどの残作業を案内します。

## ライセンス

MIT
