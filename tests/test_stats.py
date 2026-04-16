"""Tests for pretty_please.stats."""

import pytest
from pretty_please.stats import record, get_stats, tracked_transform


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

    def test_unknown_tone_ignored(self):
        record("unknown")
        assert get_stats()["total"] == 0

    def test_write_failure_is_ignored(self, monkeypatch, tmp_path):
        from pretty_please import stats

        monkeypatch.setenv("PRETTY_PLEASE_STATS_DIR", str(tmp_path))
        path = tmp_path / "stats.log"

        def fail_open(*args, **kwargs):
            raise OSError()

        monkeypatch.setattr(type(path), "open", fail_open)
        record("curt")
        assert get_stats()["total"] == 0

    def test_log_file_is_binary(self, tmp_path, monkeypatch):
        monkeypatch.setenv("PRETTY_PLEASE_STATS_DIR", str(tmp_path))
        record("curt")
        record("neutral")
        record("polite")
        data = (tmp_path / "stats.log").read_bytes()
        assert data == bytes([0x00, 0x01, 0x02])


class TestTrackedTransform:
    def test_returns_transformed_prompt(self):
        result = tracked_transform("List the planets.")
        assert result.startswith("Please, ")

    def test_records_tone(self):
        tracked_transform("List the planets.")  # curt
        tracked_transform("I need help.")  # neutral
        tracked_transform("Please help me.")  # polite
        data = get_stats()
        assert data["total"] == 3
        assert data["transformed"] == 2
        assert data["passed_through"] == 1
