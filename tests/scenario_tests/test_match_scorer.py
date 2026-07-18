"""Tests for transparent scenario scoring."""

import pytest

from intelligence.scenario_engine.match_scorer import calculate_match_score


def test_calculates_weighted_match() -> None:
    score = calculate_match_score([(0.2, "MATCH"), (0.3, "PARTIAL"), (0.5, "UNKNOWN")])

    assert score == pytest.approx(0.35)


def test_contradiction_cannot_produce_negative_score() -> None:
    assert calculate_match_score([(1.0, "CONTRADICT")]) == 0.0
