"""Tests for pretty_please.stats."""

import json
import os
import pytest
from pathlib import Path
from pretty_please.stats import record, get_stats, tracked_transform, _defaults


@pytest.fixture(autouse=True)
def isolated_stats(tmp_path, monkeypatch):
    """Redirect stats storage to a temp dir for each test."""
    monkeypatch.setenv("PRETTY_PLEASE_STATS_DIR", str(tmp_path))


class TestRecord:
    def test_increments_total(self):
        record("curt")
        assert get_stats()["total"] == 1

    def test_increments_by_tone(self):
        record("curt")
        record("neutral")
        record("polite")
        data = get_stats()
        assert data["by_tone"]["curt"] == 1
        assert data["by_tone"]["neutral"] == 1
        assert data["by_tone"]["polite"] == 1

    def test_transformed_vs_passed_through(self):
        record("curt")
        record("neutral")
        record("polite")
        data = get_stats()
        assert data["transformed"] == 2
        assert data["passed_through"] == 1

    def test_accumulates_across_calls(self):
        for _ in range(5):
            record("curt")
        assert get_stats()["by_tone"]["curt"] == 5


class TestTrackedTransform:
    def test_returns_transformed_prompt(self):
        result = tracked_transform("List the planets.")
        assert result.startswith("Please, ")

    def test_records_tone(self):
        tracked_transform("List the planets.")  # curt
        tracked_transform("I need help with something.")  # neutral
        tracked_transform("Please help me.")  # polite
        data = get_stats()
        assert data["total"] == 3
        assert data["transformed"] == 2
        assert data["passed_through"] == 1
