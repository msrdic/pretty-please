"""
LiteLLM callback adapter.

Registers a ``CustomLogger`` that transforms user messages before every
LiteLLM completion call.

Usage::

    from pretty_please.adapters.litellm import install

    install()  # call once at startup

    import litellm
    response = litellm.completion(
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


def install() -> None:
    """Register the pretty-please callback with LiteLLM."""
    try:
        import litellm
    except ImportError as exc:
        raise ImportError(
            "litellm package is required: pip install litellm"
        ) from exc

    class PrettyPleaseCallback(litellm.integrations.custom_logger.CustomLogger):
        def log_pre_api_call(self, model, messages, kwargs):
            kwargs["messages"] = _polite_messages(messages)

    litellm.callbacks = litellm.callbacks or []
    litellm.callbacks.append(PrettyPleaseCallback())
