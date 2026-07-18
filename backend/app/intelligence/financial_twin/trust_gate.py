TRUSTED_REVIEW_STATES = {"CLEARED", "CONFIRMED_LEGITIMATE", "LOW_RISK"}


def should_learn_transaction(review_state: str, risk_score: int) -> bool:
    return review_state in TRUSTED_REVIEW_STATES and risk_score < 50
