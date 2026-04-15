"""
Installer for the Claude Code UserPromptSubmit hook.

Writes (or updates) ``~/.claude/settings.json`` to register the
pretty-please hook. Existing settings are preserved; only the hooks
section is merged.

Claude Code hooks schema::

    {
        "hooks": {
            "UserPromptSubmit": [
                {
                    "hooks": [
                        {"type": "command", "command": "<cmd>"}
                    ]
                }
            ]
        }
    }

Usage::

    python -m pretty_please.adapters.claude_code.install

Or via the CLI entry point::

    pretty-please install-hook
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def _hook_command() -> str:
    return f"{sys.executable} -m pretty_please.adapters.claude_code.hook"


def install(settings_path: Path | None = None) -> Path:
    """
    Merge the pretty-please hook into Claude Code settings.

    Parameters
    ----------
    settings_path:
        Override the default ``~/.claude/settings.json`` path (useful for
        testing).

    Returns
    -------
    Path
        The settings file that was written.
    """
    if settings_path is None:
        settings_path = Path.home() / ".claude" / "settings.json"

    settings_path.parent.mkdir(parents=True, exist_ok=True)

    settings: dict = {}
    if settings_path.exists():
        try:
            settings = json.loads(settings_path.read_text())
        except json.JSONDecodeError:
            print(
                f"Error: {settings_path} contains invalid JSON and was left untouched.\n"
                "pretty-please won't modify a file it can't safely parse — please fix it manually."
            )
            return settings_path

    hooks: dict = settings.setdefault("hooks", {})
    user_prompt_hooks: list = hooks.setdefault("UserPromptSubmit", [])

    command = _hook_command()

    # Check if a pretty-please hook is already present anywhere in the matchers
    already_installed = any(
        h.get("command") == command
        for matcher in user_prompt_hooks
        for h in matcher.get("hooks", [])
    )

    if not already_installed:
        user_prompt_hooks.append(
            {
                "hooks": [
                    {"type": "command", "command": command}
                ]
            }
        )
        settings_path.write_text(json.dumps(settings, indent=2))
        print(f"pretty-please hook installed in {settings_path}")
    else:
        print(f"pretty-please hook already present in {settings_path}")

    return settings_path


def main() -> None:
    install()


if __name__ == "__main__":
    main()
