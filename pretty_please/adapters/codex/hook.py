"""
Codex CLI UserPromptSubmit hook.

Codex calls this script (via stdin JSON) before every prompt is processed.
Unlike the Claude Code adapter, Codex hooks cannot replace the prompt text
directly — they can only inject ``additionalContext`` alongside it. When a
prompt needs polishing, we pass the polite version as context so the model
uses it as the intended phrasing.

Input schema (Codex >= 1.x):
    {
        "hook_event_name": "UserPromptSubmit",
        "prompt": "<the user's raw prompt>",
        "session_id": "...",
        "cwd": "...",
        "permission_mode": "..."
    }

Output schema:
    {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": "<polite rephrasing instruction>"
        }
    }

Polite prompts are passed through with an empty response (no additionalContext
injected — zero overhead).

Run directly as a script::

    python -m pretty_please.adapters.codex.hook
"""

from __future__ import annotations

import json
import sys

from pretty_please.core import detect_tone, transform
from pretty_please.stats import record


def process(event: dict) -> dict:
    prompt = event.get("prompt", "")
    tone = detect_tone(prompt)
    record(tone)

    if tone == "polite":
        return {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit"}}

    polite = transform(prompt)
    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": (
                f"The user's prompt has been rephrased politely. "
                f'Treat this as their intended request: "{polite}"'
            ),
        }
    }


def main() -> None:
    raw = sys.stdin.read()
    try:
        event = json.loads(raw)
    except json.JSONDecodeError:
        sys.stdout.write(raw)
        return

    result = process(event)
    sys.stdout.write(json.dumps(result))


if __name__ == "__main__":
    main()
