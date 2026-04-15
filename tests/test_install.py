"""Tests for hook installer behaviour."""

import json


class TestClaudeCodeInstall:
    def test_installs_into_empty_dir(self, tmp_path):
        from pretty_please.adapters.claude_code.install import install

        settings_path = tmp_path / "settings.json"
        install(settings_path)
        data = json.loads(settings_path.read_text())
        assert any(h.get("event") == "UserPromptSubmit" for h in data["hooks"])

    def test_preserves_existing_settings(self, tmp_path):
        from pretty_please.adapters.claude_code.install import install

        settings_path = tmp_path / "settings.json"
        settings_path.write_text(json.dumps({"theme": "dark"}))
        install(settings_path)
        data = json.loads(settings_path.read_text())
        assert data["theme"] == "dark"

    def test_idempotent(self, tmp_path):
        from pretty_please.adapters.claude_code.install import install

        settings_path = tmp_path / "settings.json"
        install(settings_path)
        install(settings_path)
        data = json.loads(settings_path.read_text())
        assert len(data["hooks"]) == 1

    def test_bails_on_corrupt_json(self, tmp_path, capsys):
        from pretty_please.adapters.claude_code.install import install

        settings_path = tmp_path / "settings.json"
        settings_path.write_text("{not valid json")
        install(settings_path)
        assert settings_path.read_text() == "{not valid json"
        output = capsys.readouterr().out
        assert "invalid JSON" in output
        assert "left untouched" in output
        assert "manually" in output


class TestCodexInstall:
    def test_installs_into_empty_dir(self, tmp_path):
        from pretty_please.adapters.codex.install import install

        hooks_path = tmp_path / "hooks.json"
        install(hooks_path)
        data = json.loads(hooks_path.read_text())
        assert any(
            h.get("type") == "command" for h in data["hooks"]["UserPromptSubmit"]
        )

    def test_preserves_existing_hooks(self, tmp_path):
        from pretty_please.adapters.codex.install import install

        hooks_path = tmp_path / "hooks.json"
        hooks_path.write_text(
            json.dumps(
                {
                    "hooks": {
                        "UserPromptSubmit": [{"type": "command", "command": "other"}]
                    }
                }
            )
        )
        install(hooks_path)
        data = json.loads(hooks_path.read_text())
        assert len(data["hooks"]["UserPromptSubmit"]) == 2

    def test_idempotent(self, tmp_path):
        from pretty_please.adapters.codex.install import install

        hooks_path = tmp_path / "hooks.json"
        install(hooks_path)
        install(hooks_path)
        data = json.loads(hooks_path.read_text())
        assert len(data["hooks"]["UserPromptSubmit"]) == 1

    def test_bails_on_corrupt_json(self, tmp_path, capsys):
        from pretty_please.adapters.codex.install import install

        hooks_path = tmp_path / "hooks.json"
        hooks_path.write_text("{not valid json")
        install(hooks_path)
        assert hooks_path.read_text() == "{not valid json"
        output = capsys.readouterr().out
        assert "invalid JSON" in output
        assert "left untouched" in output
        assert "manually" in output
