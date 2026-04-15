"""End-to-end CLI tests — invoke pretty-please as a subprocess."""

import json
import subprocess
import sys


def run(*args, env=None):
    return subprocess.run(
        [sys.executable, "-m", "pretty_please.cli", *args],
        capture_output=True,
        text=True,
        env=env,
    )


class TestStatsCLI:
    def test_stats_exits_zero(self, tmp_path, monkeypatch):
        import os

        env = {**os.environ, "PRETTY_PLEASE_STATS_DIR": str(tmp_path)}
        result = run("stats", env=env)
        assert result.returncode == 0

    def test_stats_output_contains_headers(self, tmp_path):
        import os

        env = {**os.environ, "PRETTY_PLEASE_STATS_DIR": str(tmp_path)}
        result = run("stats", env=env)
        assert "Total seen" in result.stdout
        assert "Transformed" in result.stdout
        assert "Passed through" in result.stdout

    def test_stats_reflects_recorded_events(self, tmp_path):
        import os

        log = tmp_path / "stats.log"
        log.write_bytes(bytes([0x00, 0x00, 0x01, 0x02]))  # 2 curt, 1 neutral, 1 polite
        env = {**os.environ, "PRETTY_PLEASE_STATS_DIR": str(tmp_path)}
        result = run("stats", env=env)
        assert "4" in result.stdout  # total
        assert "3" in result.stdout  # transformed
        assert "1" in result.stdout  # passed through


class TestInstallHookCLI:
    def test_install_hook_claude_exits_zero(self, tmp_path):
        path = tmp_path / "settings.json"
        result = run("install-hook", "--path", str(path))
        assert result.returncode == 0

    def test_install_hook_writes_settings(self, tmp_path):
        path = tmp_path / "settings.json"
        run("install-hook", "--path", str(path))
        data = json.loads(path.read_text())
        matchers = data["hooks"]["UserPromptSubmit"]
        assert any(
            h.get("type") == "command"
            for matcher in matchers
            for h in matcher.get("hooks", [])
        )

    def test_install_hook_codex_exits_zero(self, tmp_path):
        path = tmp_path / "hooks.json"
        result = run("install-hook", "--codex", "--path", str(path))
        assert result.returncode == 0

    def test_install_hook_codex_writes_hooks(self, tmp_path):
        path = tmp_path / "hooks.json"
        run("install-hook", "--codex", "--path", str(path))
        data = json.loads(path.read_text())
        assert "UserPromptSubmit" in data["hooks"]

    def test_no_subcommand_exits_nonzero(self):
        result = run()
        assert result.returncode != 0
