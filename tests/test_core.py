"""Tests for pretty_please.core — tone detection and transformation."""

from pretty_please.core import detect_tone, transform


class TestDetectTone:
    def test_polite_please(self):
        assert detect_tone("Please summarize this.") == "polite"

    def test_polite_could_you(self):
        assert detect_tone("Could you explain this concept?") == "polite"

    def test_polite_would_you(self):
        assert detect_tone("Would you write a poem about frogs?") == "polite"

    def test_polite_kindly(self):
        assert detect_tone("Kindly provide the answer.") == "polite"

    def test_polite_can_you(self):
        assert detect_tone("Can you help me debug this?") == "polite"

    def test_curt_imperative_short(self):
        assert detect_tone("List the planets.") == "curt"

    def test_curt_imperative_explain(self):
        assert detect_tone("Explain recursion") == "curt"

    def test_curt_profanity(self):
        assert detect_tone("just tell me the damn answer") == "curt"

    def test_curt_all_caps(self):
        assert detect_tone("WRITE ME A FUNCTION") == "curt"

    def test_curt_all_caps_many_words(self):
        assert detect_tone("NASA IS WRONG ABOUT THIS") == "curt"

    def test_not_curt_few_caps_words(self):
        # Fewer than 4 consecutive all-caps words → not flagged
        assert detect_tone("I need the NASA API docs") != "curt"

    def test_not_curt_caps_acronym_in_sentence(self):
        assert detect_tone("Please SUMMARIZE this for me") == "polite"

    def test_curt_aggressive_punct(self):
        assert detect_tone("Just answer!!") == "curt"

    def test_neutral_long(self):
        tone = detect_tone(
            "I have a Python script that processes CSV files. "
            "I would like to understand how the performance could be improved."
        )
        assert tone == "neutral"

    def test_polite_can_you_write(self):
        # "can you" matches _POLITE_PATTERNS directly
        assert detect_tone("Can you write a sonnet about autumn?") == "polite"

    def test_neutral_imperative_with_modal(self):
        # Short imperative verb but softened by a modal → neutral, not curt
        assert detect_tone("Write me something, it should be short") == "neutral"


class TestTransform:
    def test_polite_passthrough(self):
        prompt = "Please write me a haiku."
        assert transform(prompt) == prompt

    def test_curt_prepend(self):
        result = transform("List the planets.")
        assert result.startswith("Please, ")
        assert "list the planets" in result.lower()

    def test_curt_lowercases_first_char(self):
        result = transform("Explain recursion")
        assert result == "Please, explain recursion"

    def test_neutral_append_no_punct(self):
        result = transform("I need help with my resume")
        assert result.endswith(", please")

    def test_neutral_append_with_period(self):
        result = transform("I need help with my resume.")
        assert result.endswith(", please.")
        assert result.count(".") == 1  # period not duplicated

    def test_neutral_append_with_question(self):
        result = transform("What is the capital of France?")
        # "What is" doesn't trigger imperative detection
        assert result.endswith(", please?") or result.endswith(", please")

    def test_profanity_prepend(self):
        result = transform("just tell me the damn answer")
        assert result.startswith("Please, ")

    def test_idempotent_polite(self):
        prompt = "Could you summarize this article?"
        assert transform(transform(prompt)) == transform(prompt)

    def test_empty_string_passthrough(self):
        assert transform("") == ""

    def test_whitespace_only_passthrough(self):
        assert transform("   ") == "   "
