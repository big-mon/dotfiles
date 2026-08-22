import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
README = (REPO_ROOT / "README.md").read_text()
AGENTS = (REPO_ROOT / "AGENTS.md").read_text()
AGENTS_MISE = REPO_ROOT / "users" / "agents" / "mise.toml"
LEGACY_GLOBAL_MISE = REPO_ROOT / "users" / "agents" / "dotfiles" / "mise" / "config.toml"
GITIGNORE = REPO_ROOT / ".gitignore"


class DocumentationBoundaryTest(unittest.TestCase):
    def test_human_admin_workflow_uses_the_isolated_clone(self):
        unsafe_brewfile = "/Users/agents/Repos/dotfiles/hosts/hermes-macos/Brewfile"

        self.assertNotIn(unsafe_brewfile, README)
        self.assertIn("/Users/estrilda/Repos/dotfiles", README)

    def test_human_setup_finishes_admin_work_before_switching_to_agents(self):
        admin_apps = README.index("## 3. 管理者が共有アプリをインストールする")
        agents_setup = README.index("## 4. `agents` がmiseを入れてリポジトリを取得する")

        self.assertLess(admin_apps, agents_setup)
        self.assertIn("ここで初めて `agents` へサインイン", README)

    def test_agent_instructions_forbid_agents_checkout_as_admin_input(self):
        self.assertIn("Never direct an administrator command to a file under `/Users/agents`", AGENTS)
        self.assertIn("/Users/estrilda/Repos/dotfiles", AGENTS)

    def test_agents_mise_config_is_the_only_pnpm_declaration(self):
        config = AGENTS_MISE.read_text()

        self.assertIn('"~/.config/mise/config.toml" = { source = "mise.toml"', config)
        self.assertIn('"~/.config/mise/mise.lock" = { source = "mise.lock"', config)
        self.assertEqual(config.count('pnpm = "'), 1)
        self.assertFalse(LEGACY_GLOBAL_MISE.exists())

    def test_generated_files_are_ignored_but_env_files_remain_visible(self):
        patterns = set(GITIGNORE.read_text().splitlines())

        self.assertTrue({".DS_Store", "__pycache__/", "*.py[cod]"} <= patterns)
        self.assertFalse(any(".env" in pattern for pattern in patterns))


if __name__ == "__main__":
    unittest.main()
