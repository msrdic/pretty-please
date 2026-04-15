"""
Prompt transformation tracking.

Stats are stored in ``~/.pretty-please/stats.json`` and persist across
sessions. Each adapter and the Claude Code hook call ``tracked_transform()``
instead of ``transform()`` directly — that's the only instrumentation needed.

CLI usage::

    pretty-please stats
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from pretty_please.core import detect_tone, transform


def _stats_path() -> Path:
    return Path(os.environ.get("PRETTY_PLEASE_STATS_DIR", Path.home() / ".pretty-please")) / "stats.json"


def _defaults() -> dict:
    return {
        "total": 0,
        "transformed": 0,
        "passed_through": 0,
        "by_tone": {"curt": 0, "neutral": 0, "polite": 0},
    }


def _load() -> dict:
    path = _stats_path()
    if path.exists():
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, KeyError):
            pass
    return _defaults()


def _save(data: dict) -> None:
    path = _stats_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2))
    tmp.replace(path)


def record(tone: str) -> None:
    """Increment counters for a prompt with the given *tone*."""
    data = _load()
    data["total"] += 1
    data["by_tone"].setdefault(tone, 0)
    data["by_tone"][tone] += 1
    if tone == "polite":
        data["passed_through"] += 1
    else:
        data["transformed"] += 1
    _save(data)


def get_stats() -> dict:
    """Return the current stats dict."""
    return _load()


def tracked_transform(prompt: str) -> str:
    """Detect tone, record it, then return the transformed prompt."""
    tone = detect_tone(prompt)
    record(tone)
    return transform(prompt)


def show() -> None:
    """Print a human-readable stats summary."""
    data = _load()
    total = data["total"]
    transformed = data["transformed"]
    passed = data["passed_through"]
    by_tone = data["by_tone"]

    def pct(n: int) -> str:
        return f"({n / total:.0%})" if total else ""

    print("pretty-please stats")
    print("─" * 30)
    print(f"Total seen:      {total:>6}")
    print(f"Transformed:     {transformed:>6}  {pct(transformed)}")
    print(f"  curt:          {by_tone.get('curt', 0):>6}")
    print(f"  neutral:       {by_tone.get('neutral', 0):>6}")
    print(f"Passed through:  {passed:>6}  {pct(passed)}")
