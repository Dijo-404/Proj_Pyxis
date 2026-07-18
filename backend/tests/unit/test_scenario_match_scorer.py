from app.intelligence.scenario_engine.match_scorer import calculate_match_score
from app.schemas.evidence import SignalEvaluation


def test_calculate_match_score_handles_partial_and_unknown_evidence():
    signals = [
        SignalEvaluation(signal="large_incoming_transaction", status="MATCH", weight=0.2),
        SignalEvaluation(signal="weak_business_explanation", status="PARTIAL", weight=0.4),
        SignalEvaluation(signal="invoice_exists", status="UNKNOWN", weight=0.4),
    ]

    assert calculate_match_score(signals) == 0.4

