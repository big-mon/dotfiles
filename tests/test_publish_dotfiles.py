import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "publish-dotfiles"


class PublishDotfilesTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.remote = self.root / "remote.git"
        self.repo = self.root / "repo"
        self.bin = self.root / "bin"
        self.bin.mkdir()

        subprocess.run(["git", "init", "--bare", str(self.remote)], check=True, capture_output=True)
        subprocess.run(["git", "init", "-b", "main", str(self.repo)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.name", "Test User"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "remote", "add", "origin", str(self.remote)], check=True)

        (self.repo / "dotfiles").mkdir()
        (self.repo / "dotfiles" / "zshrc").write_text("# initial\n")
        (self.repo / "mise.toml").write_text("[tools]\n")
        subprocess.run(["git", "-C", str(self.repo), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-m", "initial"], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(self.repo), "push", "-u", "origin", "main"], check=True, capture_output=True)

        mise = self.bin / "mise"
        mise.write_text("#!/bin/sh\nexit 0\n")
        mise.chmod(0o755)

    def tearDown(self):
        self.tempdir.cleanup()

    def run_publish(self, *args):
        env = os.environ.copy()
        env["PATH"] = f"{self.bin}:{env['PATH']}"
        return subprocess.run(
            [str(SCRIPT), *args],
            cwd=self.repo,
            env=env,
            text=True,
            capture_output=True,
        )

    def test_commits_and_pushes_reviewed_change(self):
        (self.repo / "dotfiles" / "zshrc").write_text("# updated\n")

        result = self.run_publish("Update shell settings")

        self.assertEqual(result.returncode, 0, result.stderr)
        local = subprocess.check_output(
            ["git", "-C", str(self.repo), "log", "-1", "--pretty=%s"], text=True
        ).strip()
        remote = subprocess.check_output(
            ["git", "--git-dir", str(self.remote), "log", "-1", "--pretty=%s", "main"], text=True
        ).strip()
        self.assertEqual(local, "Update shell settings")
        self.assertEqual(remote, "Update shell settings")

    def test_refuses_suspicious_untracked_file(self):
        (self.repo / ".env").write_text("TOKEN=secret\n")

        result = self.run_publish("Accidental secret")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("suspicious filename", result.stderr)
        count = subprocess.check_output(
            ["git", "-C", str(self.repo), "rev-list", "--count", "HEAD"], text=True
        ).strip()
        self.assertEqual(count, "1")

    def test_refuses_private_key_content(self):
        private_key_header = "-----BEGIN " + "OPENSSH PRIVATE KEY-----"
        (self.repo / "dotfiles" / "zshrc").write_text(
            f"{private_key_header}\nnot-a-real-key\n"
        )

        result = self.run_publish("Accidental private key")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("private key material", result.stderr)

    def test_no_changes_is_a_successful_noop(self):
        result = self.run_publish("Nothing to publish")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("No dotfiles changes to publish", result.stdout)

    def test_requires_commit_message(self):
        result = self.run_publish()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("commit message", result.stderr)

    def test_mise_exposes_publish_task(self):
        env = os.environ.copy()
        env["MISE_TRUSTED_CONFIG_PATHS"] = str(REPO_ROOT)
        result = subprocess.run(
            ["mise", "tasks"],
            cwd=REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("publish", result.stdout)


if __name__ == "__main__":
    unittest.main()
