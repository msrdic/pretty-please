"""
LiteLLM adapter.

Provides ``completion`` and ``acompletion`` wrappers around LiteLLM that
transform user messages before the API call. This is the correct approach
for library mode — LiteLLM's ``CustomLogger.log_pre_api_call`` is
observability-only and mutations there do not affect the actual request.

Usage::

    from pretty_please.adapters.litellm import completion, acompletion

    response = completion(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Explain recursion."}],
    )
"""

from __future__ import annotations

from pretty_please.core import transform


def _polite_messages(messages: list[dict]) -> list[dict]:
    result = []
    for msg in messages:
        if msg.get("role") == "user":
            content = msg["content"]
            if isinstance(content, str):
                msg = {**msg, "content": transform(content)}
        result.append(msg)
    return result


def completion(*, messages: list[dict], **kwargs):
    """Drop-in for ``litellm.completion`` with polite message transformation."""
    try:
        import litellm
    except ImportError as exc:
        raise ImportError(
            "litellm package is required: pip install litellm"
        ) from exc
    return litellm.completion(messages=_polite_messages(messages), **kwargs)


async def acompletion(*, messages: list[dict], **kwargs):
    """Drop-in for ``litellm.acompletion`` with polite message transformation."""
    try:
        import litellm
    except ImportError as exc:
        raise ImportError(
            "litellm package is required: pip install litellm"
        ) from exc
    return await litellm.acompletion(messages=_polite_messages(messages), **kwargs)
