"""
Claude Code UserPromptSubmit hook.

Claude Code calls this script (via stdin JSON) before every prompt is sent.
The hook reads the event, transforms the prompt, and writes back JSON.

Hook event schema (Claude Code >= 1.x):
    {
        "hook_event_name": "UserPromptSubmit",
        "prompt": "<the user's raw prompt>"
    }

Response schema:
    {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "transformedPrompt": "<polite prompt>"
        }
    }

This module can be run directly as a script::

    python -m pretty_please.adapters.claude_code.hook

Or referenced by path in ``~/.claude/settings.json``.
"""

from __future__ import annotations

import json
import sys

from pretty_please.core import transform


def process(event: dict) -> dict:
    prompt = event.get("prompt", "")
    polite = transform(prompt)
    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "transformedPrompt": polite,
        }
    }


def main() -> None:
    raw = sys.stdin.read()
    try:
        event = json.loads(raw)
    except json.JSONDecodeError:
        # If we can't parse the event, pass through unchanged
        sys.stdout.write(raw)
        return

    result = process(event)
    sys.stdout.write(json.dumps(result))


if __name__ == "__main__":
    main()
