from app.schemas.evidence import SignalEvaluation


STATUS_MULTIPLIERS = {
    "MATCH": 1.0,
    "PARTIAL": 0.5,
    "UNKNOWN": 0.0,
    "CONTRADICT": -0.5,
}


def calculate_match_score(signals: list[SignalEvaluation]) -> float:
    total_weight = sum(signal.weight for signal in signals)
    if total_weight == 0:
        return 0
    weighted = sum(signal.weight * STATUS_MULTIPLIERS[signal.status] for signal in signals)
    return round(max(0, min(1, weighted / total_weight)), 2)

