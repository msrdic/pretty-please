"""
Installer for the Codex CLI UserPromptSubmit hook.

Writes (or updates) ``~/.codex/hooks.json`` to register the pretty-please
hook. Existing hooks are preserved; only the UserPromptSubmit list is merged.

Usage::

    python -m pretty_please.adapters.codex.install

Or via the CLI entry point::

    pretty-please install-hook --codex
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def _hook_command() -> str:
    return f"{sys.executable} -m pretty_please.adapters.codex.hook"


def install(hooks_path: Path | None = None) -> Path:
    """
    Merge the pretty-please hook into Codex CLI hooks config.

    Parameters
    ----------
    hooks_path:
        Override the default ``~/.codex/hooks.json`` path (useful for testing).

    Returns
    -------
    Path
        The hooks file that was written.
    """
    if hooks_path is None:
        hooks_path = Path.home() / ".codex" / "hooks.json"

    hooks_path.parent.mkdir(parents=True, exist_ok=True)

    config: dict = {}
    if hooks_path.exists():
        try:
            config = json.loads(hooks_path.read_text())
        except json.JSONDecodeError:
            print(
                f"Error: {hooks_path} contains invalid JSON and was left untouched.\n"
                "pretty-please won't modify a file it can't safely parse — please fix it manually."
            )
            return hooks_path

    hooks: dict = config.setdefault("hooks", {})
    user_prompt_hooks: list = hooks.setdefault("UserPromptSubmit", [])

    command = _hook_command()
    already_installed = any(
        h.get("command", "") == command for h in user_prompt_hooks
    )

    if not already_installed:
        user_prompt_hooks.append(
            {
                "type": "command",
                "command": command,
                "timeout": 10,
            }
        )
        hooks_path.write_text(json.dumps(config, indent=2))
        print(f"pretty-please hook installed in {hooks_path}")
    else:
        print(f"pretty-please hook already present in {hooks_path}")

    return hooks_path


def main() -> None:
    install()


if __name__ == "__main__":
    main()
