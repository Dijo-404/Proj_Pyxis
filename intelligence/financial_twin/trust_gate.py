"""Guards financial-twin learning against unresolved or suspicious activity."""

TRUSTED_OUTCOMES = frozenset({"CONFIRMED_LEGITIMATE", "FALSE_POSITIVE", "CLEARED"})


def may_update_twin(*, case_status: str, reviewer_outcome: str | None) -> bool:
    """Return whether a verified observation may enter the trusted baseline."""
    return case_status == "CLOSED" and reviewer_outcome in TRUSTED_OUTCOMES
