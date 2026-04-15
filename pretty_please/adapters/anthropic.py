"""
Anthropic SDK adapter.

Wraps ``anthropic.Anthropic`` so that every ``messages.create`` call
has its prompt politely transformed before it reaches the API.

Usage::

    from pretty_please.adapters.anthropic import PrettyAnthropicClient

    client = PrettyAnthropicClient()
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": "Summarize this article."}],
    )
"""

from __future__ import annotations

from pretty_please.stats import tracked_transform as transform


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


class _PrettyMessages:
    def __init__(self, messages):
        self._messages = messages

    def create(self, *, messages: list[dict], **kwargs):
        return self._messages.create(messages=_polite_messages(messages), **kwargs)

    def stream(self, *, messages: list[dict], **kwargs):
        return self._messages.stream(messages=_polite_messages(messages), **kwargs)


class PrettyAnthropicClient:
    """Drop-in replacement for ``anthropic.Anthropic`` with polite prompts."""

    def __init__(self, **kwargs):
        try:
            import anthropic
        except ImportError as exc:
            raise ImportError(
                "anthropic package is required: pip install anthropic"
            ) from exc
        self._client = anthropic.Anthropic(**kwargs)
        self.messages = _PrettyMessages(self._client.messages)

    def __getattr__(self, name: str):
        return getattr(self._client, name)
