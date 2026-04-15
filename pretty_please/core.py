"""
Core tone detection and prompt transformation logic.
Zero external dependencies — stdlib only.
"""

import re

# Polite markers: user already said please (or equivalent)
_POLITE_PATTERNS = re.compile(
    r"\b(please|could you|would you|kindly|can you)\b",
    re.IGNORECASE,
)

# Imperative verbs that commonly open curt prompts
_IMPERATIVE_VERBS = re.compile(
    r"^(write|list|give|tell|show|explain|describe|summarize|translate|"
    r"fix|find|create|generate|make|get|fetch|run|check|analyze|compare|"
    r"define|name|provide|convert|calculate|count|sort|format|print|"
    r"produce|draw|suggest|recommend|build|implement|add|remove|delete|"
    r"update|send|return)\b",
    re.IGNORECASE,
)

# Modal verbs that soften imperatives
_MODAL_VERBS = re.compile(
    r"\b(can|could|will|would|shall|should|may|might|must)\b",
    re.IGNORECASE,
)

# Rudeness signals
_PROFANITY = re.compile(
    r"\b(damn|hell|crap|stupid|idiot|dumb|shut up|wtf|wth|ass|bastard)\b",
    re.IGNORECASE,
)
_AGGRESSIVE_PUNCT = re.compile(r"[!?]{2,}|[A-Z]{5,}")


def detect_tone(prompt: str) -> str:
    """
    Classify a prompt as 'polite', 'curt', or 'neutral'.

    Returns
    -------
    str
        One of 'polite', 'curt', or 'neutral'.
    """
    stripped = prompt.strip()

    if _POLITE_PATTERNS.search(stripped):
        return "polite"

    if _PROFANITY.search(stripped) or _AGGRESSIVE_PUNCT.search(stripped):
        return "curt"

    # Short prompt that starts with an imperative verb and lacks a modal → curt-ish
    if len(stripped.split()) <= 12 and _IMPERATIVE_VERBS.match(stripped):
        if not _MODAL_VERBS.search(stripped):
            return "curt"

    return "neutral"


def transform(prompt: str) -> str:
    """
    Inject politeness into *prompt* based on detected tone.

    Rules
    -----
    - polite   → returned unchanged
    - curt     → "Please, " prepended
    - neutral  → ", please" appended (with smart punctuation handling)
    """
    if not prompt.strip():
        return prompt

    tone = detect_tone(prompt)

    if tone == "polite":
        return prompt

    if tone == "curt":
        return "Please, " + prompt[0].lower() + prompt[1:]

    # neutral: append ", please" before any trailing punctuation
    stripped = prompt.rstrip()
    trailing_punct = prompt[len(stripped):]  # whitespace after text, if any
    text = stripped

    if text and text[-1] in ".!?":
        # Insert before the final punctuation mark
        return text[:-1] + ", please" + text[-1] + trailing_punct
    else:
        return text + ", please" + trailing_punct
