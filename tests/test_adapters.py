"""Tests for pretty_please adapters (no real API calls)."""

import pytest
from unittest.mock import MagicMock, patch


class TestAnthropicAdapter:
    def test_transforms_user_message(self):
        mock_anthropic = MagicMock()
        mock_anthropic.Anthropic.return_value.messages = MagicMock()

        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            from pretty_please.adapters.anthropic import (
                PrettyAnthropicClient,
                _polite_messages,
            )

            messages = [{"role": "user", "content": "List the planets."}]
            result = _polite_messages(messages)
            assert result[0]["content"].startswith("Please, ")

    def test_leaves_assistant_message_unchanged(self):
        with patch.dict("sys.modules", {"anthropic": MagicMock()}):
            from pretty_please.adapters.anthropic import _polite_messages

            messages = [
                {"role": "assistant", "content": "Here are the planets."},
            ]
            result = _polite_messages(messages)
            assert result[0]["content"] == "Here are the planets."

    def test_transforms_content_block(self):
        with patch.dict("sys.modules", {"anthropic": MagicMock()}):
            from pretty_please.adapters.anthropic import _polite_messages

            messages = [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": "Explain gravity."}],
                }
            ]
            result = _polite_messages(messages)
            assert result[0]["content"][0]["text"].startswith("Please, ")


class TestOpenAIAdapter:
    def test_transforms_user_message(self):
        with patch.dict("sys.modules", {"openai": MagicMock()}):
            from pretty_please.adapters.openai import _polite_messages

            messages = [{"role": "user", "content": "Write a haiku."}]
            result = _polite_messages(messages)
            assert result[0]["content"].startswith("Please, ")

    def test_leaves_system_message_unchanged(self):
        with patch.dict("sys.modules", {"openai": MagicMock()}):
            from pretty_please.adapters.openai import _polite_messages

            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Write a haiku."},
            ]
            result = _polite_messages(messages)
            assert result[0]["content"] == "You are a helpful assistant."
            assert result[1]["content"].startswith("Please, ")


class TestLiteLLMAdapter:
    def test_transforms_user_message(self):
        from pretty_please.adapters.litellm import _polite_messages

        messages = [{"role": "user", "content": "Explain recursion."}]
        result = _polite_messages(messages)
        assert result[0]["content"].startswith("Please, ")

    def test_leaves_system_message_unchanged(self):
        from pretty_please.adapters.litellm import _polite_messages

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Explain recursion."},
        ]
        result = _polite_messages(messages)
        assert result[0]["content"] == "You are a helpful assistant."
        assert result[1]["content"].startswith("Please, ")

    def test_completion_passes_polite_messages(self):
        mock_litellm = MagicMock()
        with patch.dict("sys.modules", {"litellm": mock_litellm}):
            from pretty_please.adapters import litellm as adapter
            import importlib
            importlib.reload(adapter)

            adapter.completion(model="gpt-4o", messages=[{"role": "user", "content": "List planets."}])
            call_messages = mock_litellm.completion.call_args[1]["messages"]
            assert call_messages[0]["content"].startswith("Please, ")


class TestClaudeCodeHook:
    def test_hook_transforms_prompt(self):
        from pretty_please.adapters.claude_code.hook import process

        event = {"hook_event_name": "UserPromptSubmit", "prompt": "List the planets."}
        result = process(event)
        transformed = result["hookSpecificOutput"]["transformedPrompt"]
        assert transformed.startswith("Please, ")

    def test_hook_passes_through_polite(self):
        from pretty_please.adapters.claude_code.hook import process

        event = {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "Please list the planets.",
        }
        result = process(event)
        transformed = result["hookSpecificOutput"]["transformedPrompt"]
        assert transformed == "Please list the planets."

    def test_hook_empty_prompt(self):
        from pretty_please.adapters.claude_code.hook import process

        event = {"hook_event_name": "UserPromptSubmit", "prompt": ""}
        result = process(event)
        assert "transformedPrompt" in result["hookSpecificOutput"]


class TestCodexHook:
    def test_curt_prompt_injects_additional_context(self):
        from pretty_please.adapters.codex.hook import process

        event = {"hook_event_name": "UserPromptSubmit", "prompt": "List the planets."}
        result = process(event)
        context = result["hookSpecificOutput"].get("additionalContext", "")
        assert "Please, list the planets." in context

    def test_polite_prompt_has_no_additional_context(self):
        from pretty_please.adapters.codex.hook import process

        event = {"hook_event_name": "UserPromptSubmit", "prompt": "Please list the planets."}
        result = process(event)
        assert "additionalContext" not in result["hookSpecificOutput"]

    def test_hook_event_name_present(self):
        from pretty_please.adapters.codex.hook import process

        event = {"hook_event_name": "UserPromptSubmit", "prompt": "Explain gravity."}
        result = process(event)
        assert result["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
