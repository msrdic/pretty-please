"""
Installer for the Claude Code UserPromptSubmit hook.

Writes (or updates) ``~/.claude/settings.json`` to register the
pretty-please hook. Existing settings are preserved; only the hooks
section is merged.

Usage::

    python -m pretty_please.adapters.claude_code.install

Or via the CLI entry point (if installed)::

    pretty-please install-hook
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path


def _hook_command() -> str:
    python = shutil.which("python3") or shutil.which("python") or sys.executable
    return f"{python} -m pretty_please.adapters.claude_code.hook"


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

    hooks: list[dict] = settings.setdefault("hooks", [])

    # Check if a pretty-please hook already exists
    command = _hook_command()
    already_installed = any(
        hook.get("command", "") == command for hook in hooks
    )

    if not already_installed:
        hooks.append(
            {
                "event": "UserPromptSubmit",
                "command": command,
            }
        )
        settings["hooks"] = hooks
        settings_path.write_text(json.dumps(settings, indent=2))
        print(f"pretty-please hook installed in {settings_path}")
    else:
        print(f"pretty-please hook already present in {settings_path}")

    return settings_path


def main() -> None:
    install()


if __name__ == "__main__":
    main()
