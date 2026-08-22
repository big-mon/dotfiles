import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "snapshot-agents-dotfiles"


class SnapshotAgentsDotfilesTest(unittest.TestCase):
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

        self.agents = self.repo / "users" / "agents"
        (self.agents / "dotfiles").mkdir(parents=True)
        (self.agents / "dotfiles" / "zshrc").write_text("# initial\n")
        (self.agents / "mise.toml").write_text("[tools]\n")
        (self.repo / "README.md").write_text("# Initial documentation\n")
        (self.repo / "tests").mkdir()
        (self.repo / "tests" / "test_smoke.py").write_text(
            "import unittest\n\n"
            "class SmokeTest(unittest.TestCase):\n"
            "    def test_smoke(self):\n"
            "        self.assertTrue(True)\n"
        )
        subprocess.run(["git", "-C", str(self.repo), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-m", "initial"], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(self.repo), "push", "-u", "origin", "main"], check=True, capture_output=True)

        mise = self.bin / "mise"
        mise.write_text(
            '#!/bin/sh\n'
            'printf "%s\\n" "$*" >> "$MISE_LOG"\n'
            'if [ "${MISE_FAIL_STATUS:-}" = "1" ]; then\n'
            '    case "$*" in *"bootstrap status --missing"*) exit 1 ;; esac\n'
            'fi\n'
        )
        mise.chmod(0o755)
        self.mise_log = self.root / "mise.log"

    def tearDown(self):
        self.tempdir.cleanup()

    def run_snapshot(self, *args, **env_overrides):
        env = os.environ.copy()
        env["PATH"] = f"{self.bin}:{env['PATH']}"
        env["MISE_LOG"] = str(self.mise_log)
        env["MISE_BIN"] = str(self.bin / "mise")
        env.update(env_overrides)
        return subprocess.run(
            [str(SCRIPT), *args],
            cwd=self.repo,
            env=env,
            text=True,
            capture_output=True,
        )

    def test_commits_and_pushes_reviewed_change(self):
        (self.agents / "dotfiles" / "zshrc").write_text("# updated\n")

        result = self.run_snapshot("Update shell settings")

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
        (self.agents / "dotfiles" / ".env").write_text("TOKEN=secret\n")

        result = self.run_snapshot("Accidental secret")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("suspicious filename", result.stderr)
        count = subprocess.check_output(
            ["git", "-C", str(self.repo), "rev-list", "--count", "HEAD"], text=True
        ).strip()
        self.assertEqual(count, "1")

    def test_refuses_private_key_content(self):
        private_key_header = "-----BEGIN " + "OPENSSH PRIVATE KEY-----"
        (self.agents / "dotfiles" / "zshrc").write_text(
            f"{private_key_header}\nnot-a-real-key\n"
        )

        result = self.run_snapshot("Accidental private key")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("private key material", result.stderr)

    def test_refuses_change_outside_agents_dotfiles(self):
        (self.repo / "README.md").write_text("unexpected documentation change\n")

        result = self.run_snapshot("Do not publish repository metadata")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("outside users/agents/dotfiles", result.stderr)
        count = subprocess.check_output(
            ["git", "-C", str(self.repo), "rev-list", "--count", "HEAD"], text=True
        ).strip()
        self.assertEqual(count, "1")

    def test_refuses_rename_from_outside_into_agents_dotfiles(self):
        destination = self.agents / "dotfiles" / "README.md"
        subprocess.run(
            ["git", "-C", str(self.repo), "mv", "README.md", str(destination)],
            check=True,
        )

        result = self.run_snapshot("Do not hide metadata in a rename")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("outside users/agents/dotfiles: README.md", result.stderr)
        count = subprocess.check_output(
            ["git", "-C", str(self.repo), "rev-list", "--count", "HEAD"], text=True
        ).strip()
        self.assertEqual(count, "1")

    def test_refuses_non_main_branch_before_commit(self):
        subprocess.run(
            ["git", "-C", str(self.repo), "switch", "-c", "scratch"],
            check=True,
            capture_output=True,
        )
        (self.agents / "dotfiles" / "zshrc").write_text("# updated\n")

        result = self.run_snapshot("Wrong branch")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("snapshot requires branch main", result.stderr)
        count = subprocess.check_output(
            ["git", "-C", str(self.repo), "rev-list", "--count", "HEAD"], text=True
        ).strip()
        self.assertEqual(count, "1")

    def test_refuses_detached_head_before_commit(self):
        subprocess.run(
            ["git", "-C", str(self.repo), "switch", "--detach"],
            check=True,
            capture_output=True,
        )
        (self.agents / "dotfiles" / "zshrc").write_text("# updated\n")

        result = self.run_snapshot("Detached head")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("detached HEAD", result.stderr)
        count = subprocess.check_output(
            ["git", "-C", str(self.repo), "rev-list", "--count", "HEAD"], text=True
        ).strip()
        self.assertEqual(count, "1")

    def test_pushes_origin_main_without_push_default(self):
        subprocess.run(
            ["git", "-C", str(self.repo), "config", "push.default", "nothing"],
            check=True,
        )
        (self.agents / "dotfiles" / "zshrc").write_text("# updated\n")

        result = self.run_snapshot("Explicit main push")

        self.assertEqual(result.returncode, 0, result.stderr)
        remote = subprocess.check_output(
            ["git", "--git-dir", str(self.remote), "log", "-1", "--pretty=%s", "main"], text=True
        ).strip()
        self.assertEqual(remote, "Explicit main push")

    def test_pushes_origin_main_without_upstream(self):
        subprocess.run(
            ["git", "-C", str(self.repo), "config", "--unset", "branch.main.remote"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(self.repo), "config", "--unset", "branch.main.merge"],
            check=True,
        )
        (self.agents / "dotfiles" / "zshrc").write_text("# updated\n")

        result = self.run_snapshot("Explicit push without upstream")

        self.assertEqual(result.returncode, 0, result.stderr)
        remote = subprocess.check_output(
            ["git", "--git-dir", str(self.remote), "log", "-1", "--pretty=%s", "main"], text=True
        ).strip()
        self.assertEqual(remote, "Explicit push without upstream")

    def test_no_changes_is_a_successful_noop(self):
        result = self.run_snapshot("Nothing to snapshot")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("No agents dotfiles changes to snapshot", result.stdout)

    def test_does_not_write_python_bytecode(self):
        (self.agents / "dotfiles" / "zshrc").write_text("# updated\n")

        result = self.run_snapshot("Avoid Python bytecode")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.repo / "tests" / "__pycache__").exists())

    def test_pins_cron_paths_and_avoids_nonportable_sort(self):
        script = SCRIPT.read_text()

        self.assertIn('export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"', script)
        self.assertIn('mise_bin="${MISE_BIN:-$HOME/.local/bin/mise}"', script)
        self.assertIn('python_bin="${PYTHON_BIN:-/usr/bin/python3}"', script)
        self.assertIn('"$python_bin" -B -m unittest discover -s tests -v', script)
        self.assertNotIn("sort -zu", script)

    def test_missing_mise_fails_with_command_not_found_status(self):
        (self.agents / "dotfiles" / "zshrc").write_text("# updated\n")

        result = self.run_snapshot("Missing mise", MISE_BIN="/missing/mise")

        self.assertEqual(result.returncode, 127)
        self.assertIn("mise not found or not executable", result.stderr)

    def test_requires_commit_message(self):
        result = self.run_snapshot()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("commit message", result.stderr)

    def test_validates_the_agents_mise_config(self):
        (self.agents / "dotfiles" / "zshrc").write_text("# updated\n")

        result = self.run_snapshot("Validate account config")

        self.assertEqual(result.returncode, 0, result.stderr)
        calls = self.mise_log.read_text()
        agents_config = self.agents.resolve()
        self.assertIn(f"-C {agents_config} fmt --check", calls)
        self.assertIn(f"-C {agents_config} bootstrap status --missing", calls)

    def test_mise_status_failure_blocks_commit(self):
        (self.agents / "dotfiles" / "zshrc").write_text("# updated\n")

        result = self.run_snapshot("Do not commit missing state", MISE_FAIL_STATUS="1")

        self.assertNotEqual(result.returncode, 0)
        count = subprocess.check_output(
            ["git", "-C", str(self.repo), "rev-list", "--count", "HEAD"], text=True
        ).strip()
        self.assertEqual(count, "1")

if __name__ == "__main__":
    unittest.main()
