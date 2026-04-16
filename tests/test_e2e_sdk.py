"""
E2E tests for SDK adapters — require real API keys.

Skipped automatically when the relevant env var is absent:
  ANTHROPIC_API_KEY  → Anthropic tests
  OPENAI_API_KEY     → OpenAI tests + LiteLLM tests (routed via OpenAI)

Run all e2e tests:
  pytest -m e2e

Run only one provider:
  pytest -m e2e -k anthropic
  pytest -m e2e -k openai
  pytest -m e2e -k litellm
"""

import os

import pytest

pytestmark = pytest.mark.e2e


# ---------------------------------------------------------------------------
# Anthropic
# ---------------------------------------------------------------------------

anthropic_key = pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set",
)


@anthropic_key
def test_anthropic_transforms_and_gets_response():
    from pretty_please.adapters.anthropic import PrettyAnthropicClient

    client = PrettyAnthropicClient()
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=64,
        messages=[{"role": "user", "content": "Say the word OK and nothing else."}],
    )
    assert response.content[0].text.strip()


@anthropic_key
def test_anthropic_polite_prompt_not_double_transformed():
    from pretty_please.adapters.anthropic import PrettyAnthropicClient, _polite_messages

    messages = [{"role": "user", "content": "Please say OK and nothing else."}]
    transformed = _polite_messages(messages)
    # Already polite — should not gain a second "Please,"
    content = transformed[0]["content"]
    assert content.lower().count("please") == 1

    client = PrettyAnthropicClient()
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=64,
        messages=messages,
    )
    assert response.content[0].text.strip()


@anthropic_key
def test_anthropic_content_block_messages():
    from pretty_please.adapters.anthropic import PrettyAnthropicClient

    client = PrettyAnthropicClient()
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=64,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Say the word OK and nothing else."}
                ],
            }
        ],
    )
    assert response.content[0].text.strip()


# ---------------------------------------------------------------------------
# OpenAI
# ---------------------------------------------------------------------------

openai_key = pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set",
)


@openai_key
def test_openai_transforms_and_gets_response():
    from pretty_please.adapters.openai import PrettyOpenAIClient

    client = PrettyOpenAIClient()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say the word OK and nothing else."}],
        max_tokens=16,
    )
    assert response.choices[0].message.content.strip()


@openai_key
def test_openai_polite_prompt_not_double_transformed():
    from pretty_please.adapters.openai import _polite_messages

    messages = [{"role": "user", "content": "Please say OK and nothing else."}]
    transformed = _polite_messages(messages)
    content = transformed[0]["content"]
    assert content.lower().count("please") == 1

    from pretty_please.adapters.openai import PrettyOpenAIClient

    client = PrettyOpenAIClient()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=16,
    )
    assert response.choices[0].message.content.strip()


@openai_key
def test_openai_system_message_untouched():
    from pretty_please.adapters.openai import PrettyOpenAIClient

    client = PrettyOpenAIClient()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say the word OK and nothing else."},
        ],
        max_tokens=16,
    )
    assert response.choices[0].message.content.strip()


# ---------------------------------------------------------------------------
# LiteLLM (routed via OpenAI)
# ---------------------------------------------------------------------------

litellm_key = pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set (required for LiteLLM e2e tests)",
)


@litellm_key
def test_litellm_completion_transforms_and_gets_response():
    from pretty_please.adapters.litellm import completion

    response = completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say the word OK and nothing else."}],
        max_tokens=16,
    )
    assert response.choices[0].message.content.strip()


@litellm_key
def test_litellm_completion_polite_prompt_not_double_transformed():
    from pretty_please.adapters.litellm import _polite_messages, completion

    messages = [{"role": "user", "content": "Please say OK and nothing else."}]
    transformed = _polite_messages(messages)
    assert transformed[0]["content"].lower().count("please") == 1

    response = completion(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=16,
    )
    assert response.choices[0].message.content.strip()


@litellm_key
def test_litellm_completion_system_message_untouched():
    from pretty_please.adapters.litellm import completion

    response = completion(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say the word OK and nothing else."},
        ],
        max_tokens=16,
    )
    assert response.choices[0].message.content.strip()


@litellm_key
def test_litellm_acompletion_transforms_and_gets_response():
    import asyncio

    from pretty_please.adapters.litellm import acompletion

    async def _run():
        return await acompletion(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say the word OK and nothing else."}],
            max_tokens=16,
        )

    response = asyncio.run(_run())
    assert response.choices[0].message.content.strip()
