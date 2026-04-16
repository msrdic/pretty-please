"""
Prompt transformation tracking.

Each event is recorded as a single byte appended to an append-only binary
log at ``~/.pretty-please/stats.log``. Single-byte O_APPEND writes are
atomic on local POSIX filesystems — no locking, no read-modify-write race.

Encoding:
    0x00 = curt
    0x01 = neutral
    0x02 = polite

Derived at read time:
    transformed  = curt + neutral
    passed       = polite

CLI usage::

    pretty-please stats
"""

from __future__ import annotations

import collections
import os
from pathlib import Path

from pretty_please.core import detect_tone, transform

# Tone → byte encoding
_TONE_BYTE: dict[str, int] = {
    "curt": 0x00,
    "neutral": 0x01,
    "polite": 0x02,
}
_BYTE_TONE = {v: k for k, v in _TONE_BYTE.items()}


def _log_path() -> Path:
    return (
        Path(os.environ.get("PRETTY_PLEASE_STATS_DIR", Path.home() / ".pretty-please"))
        / "stats.log"
    )


def record(tone: str) -> None:
    """Append a single byte encoding *tone* to the stats log."""
    byte = _TONE_BYTE.get(tone)
    if byte is None:
        return
    path = _log_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("ab") as f:
            f.write(bytes([byte]))
    except OSError:
        # Hooks should never fail just because telemetry can't be recorded.
        return


def get_stats() -> dict:
    """Return a summary dict derived from the stats log."""
    path = _log_path()
    counts: collections.Counter = collections.Counter()
    if path.exists():
        counts = collections.Counter(path.read_bytes())

    curt = counts[_TONE_BYTE["curt"]]
    neutral = counts[_TONE_BYTE["neutral"]]
    polite = counts[_TONE_BYTE["polite"]]
    return {
        "total": curt + neutral + polite,
        "transformed": curt + neutral,
        "passed_through": polite,
        "by_tone": {"curt": curt, "neutral": neutral, "polite": polite},
    }


def tracked_transform(prompt: str) -> str:
    """Detect tone, record it, then return the transformed prompt."""
    tone = detect_tone(prompt)
    record(tone)
    return transform(prompt)


def show() -> None:
    """Print a human-readable stats summary."""
    data = get_stats()
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
    print(f"  curt:          {by_tone['curt']:>6}")
    print(f"  neutral:       {by_tone['neutral']:>6}")
    print(f"Passed through:  {passed:>6}  {pct(passed)}")

    from pretty_please.creature import get_profile

    profile = get_profile(data)
    print()
    print(f"  {profile['name']}")
    print(f"  {profile['description']}")
