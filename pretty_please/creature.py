"""Prompting style profiles based on tone distribution."""

from __future__ import annotations

_PROFILES: dict[str, dict] = {
    "commander": {
        "name": "THE COMMANDER",
        "description": "Terse and direct. You know what you want and you say it fast. pretty-please adds the polish.",
    },
    "realist": {
        "name": "THE REALIST",
        "description": "A mix of sharp and measured. Context-dependent — sometimes curt, sometimes considered.",
    },
    "pragmatist": {
        "name": "THE PRAGMATIST",
        "description": "Clear and neutral. You write to get things done, not to impress. Solid baseline.",
    },
    "taskmaster": {
        "name": "THE TASKMASTER",
        "description": "Neutral-leaning but with a brisk streak. Business as usual, with occasional edge.",
    },
    "diplomat": {
        "name": "THE DIPLOMAT",
        "description": "Naturally courteous. You rarely need intervention — the please is already there.",
    },
}


def classify_style(data: dict) -> str:
    """Classify prompting style based on tone distribution.

    Uses dominant tone + proximity ratio to distinguish 5 archetypes:
      - diplomat:   polite is dominant
      - commander:  curt is dominant and clearly > neutral (ratio >= 2x)
      - realist:    curt is dominant but close to neutral (ratio < 2x)
      - pragmatist: neutral is dominant and clearly > curt (ratio >= 2x)
      - taskmaster: neutral is dominant but close to curt (ratio < 2x)
    """
    total = data["total"]
    if total == 0:
        return "pragmatist"

    curt = data["by_tone"]["curt"]
    neutral = data["by_tone"]["neutral"]
    polite = data["by_tone"]["polite"]

    dominant = max((curt, "curt"), (neutral, "neutral"), (polite, "polite"))[1]

    if dominant == "polite":
        return "diplomat"

    if dominant == "curt":
        other = neutral if neutral > 0 else 1
        return "commander" if curt / other >= 2.0 else "realist"

    # dominant == "neutral"
    other = curt if curt > 0 else 1
    return "pragmatist" if neutral / other >= 2.0 else "taskmaster"


def get_profile(data: dict) -> dict:
    """Return the profile dict for the given stats data."""
    return _PROFILES[classify_style(data)]
