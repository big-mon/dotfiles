import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
README = (REPO_ROOT / "README.md").read_text()
AGENTS = (REPO_ROOT / "AGENTS.md").read_text()


class DocumentationBoundaryTest(unittest.TestCase):
    def test_human_admin_workflow_uses_the_isolated_clone(self):
        unsafe_brewfile = "/Users/agents/Repos/dotfiles/hosts/hermes-macos/Brewfile"

        self.assertNotIn(unsafe_brewfile, README)
        self.assertIn("/Users/estrilda/Repos/dotfiles", README)

    def test_agent_instructions_forbid_agents_checkout_as_admin_input(self):
        self.assertIn("Never direct an administrator command to a file under `/Users/agents`", AGENTS)
        self.assertIn("/Users/estrilda/Repos/dotfiles", AGENTS)


if __name__ == "__main__":
    unittest.main()
