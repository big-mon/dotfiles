import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ZSHRC = REPO_ROOT / "users" / "agents" / "dotfiles" / "zshrc"


class ZshrcTest(unittest.TestCase):
    def test_homebrew_shell_helpers_are_optional(self):
        content = ZSHRC.read_text()

        self.assertIn(
            '[[ -r "$autosuggestions" ]] && source "$autosuggestions"', content
        )
        self.assertIn(
            '[[ -r "$syntax_highlighting" ]] && source "$syntax_highlighting"',
            content,
        )

    def test_syntax_highlighting_is_loaded_last(self):
        lines = [line for line in ZSHRC.read_text().splitlines() if line.strip()]

        self.assertEqual(
            lines[-1],
            '[[ -r "$syntax_highlighting" ]] && source "$syntax_highlighting"',
        )

    def test_raises_a_low_file_limit(self):
        command = f'ulimit -n 1024; source "{ZSHRC}"; ulimit -n'
        result = subprocess.run(
            ["/bin/zsh", "-fc", command],
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertEqual(result.stdout.strip().splitlines()[-1], "4096")

    def test_does_not_lower_an_existing_high_file_limit(self):
        command = f'ulimit -n 8192; source "{ZSHRC}"; ulimit -n'
        result = subprocess.run(
            ["/bin/zsh", "-fc", command],
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertEqual(result.stdout.strip().splitlines()[-1], "8192")


if __name__ == "__main__":
    unittest.main()
