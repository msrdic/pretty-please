"""
OpenAI SDK adapter.

Wraps ``openai.OpenAI`` so that every ``chat.completions.create`` call
has its prompt politely transformed before it reaches the API.

Usage::

    from pretty_please.adapters.openai import PrettyOpenAIClient

    client = PrettyOpenAIClient()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "List the planets."}],
    )
"""

from __future__ import annotations

from pretty_please.core import transform


def _polite_messages(messages: list[dict]) -> list[dict]:
    """Return a copy of *messages* with user turns politely transformed."""
    result = []
    for msg in messages:
        if msg.get("role") == "user":
            content = msg["content"]
            if isinstance(content, str):
                msg = {**msg, "content": transform(content)}
            elif isinstance(content, list):
                new_parts = []
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        part = {**part, "text": transform(part["text"])}
                    new_parts.append(part)
                msg = {**msg, "content": new_parts}
        result.append(msg)
    return result


class _PrettyCompletions:
    def __init__(self, completions):
        self._completions = completions

    def create(self, *, messages: list[dict], **kwargs):
        return self._completions.create(
            messages=_polite_messages(messages), **kwargs
        )


class _PrettyChat:
    def __init__(self, chat):
        self.completions = _PrettyCompletions(chat.completions)


class PrettyOpenAIClient:
    """Drop-in replacement for ``openai.OpenAI`` with polite prompts."""

    def __init__(self, **kwargs):
        try:
            import openai
        except ImportError as exc:
            raise ImportError(
                "openai package is required: pip install openai"
            ) from exc
        self._client = openai.OpenAI(**kwargs)
        self.chat = _PrettyChat(self._client.chat)

    def __getattr__(self, name: str):
        return getattr(self._client, name)
