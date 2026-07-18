"""Transparent weighted scenario match calculation."""

from collections.abc import Iterable

STATE_FACTORS = {
    "MATCH": 1.0,
    "PARTIAL": 0.5,
    "UNKNOWN": 0.0,
    "CONTRADICT": -1.0,
}


def calculate_match_score(signals: Iterable[tuple[float, str]]) -> float:
    """Return a clamped 0..1 match score for weighted evidence states."""
    weighted_total = 0.0
    total_weight = 0.0
    for weight, state in signals:
        if weight <= 0:
            raise ValueError("signal weights must be positive")
        try:
            factor = STATE_FACTORS[state]
        except KeyError as error:
            raise ValueError(f"unsupported evidence state: {state}") from error
        total_weight += weight
        weighted_total += weight * factor

    if total_weight == 0:
        return 0.0
    return max(0.0, min(1.0, weighted_total / total_weight))
