from backend.app.intelligence.evidence_engine.critical_evidence import find_decision_critical_evidence
from backend.app.schemas.evidence import EvidenceComparison, SignalEvaluation


def test_find_decision_critical_evidence_prioritizes_unknown_high_weight_signal():
    comparison = EvidenceComparison(
        scenario_id="SCN-1",
        match_score=0.84,
        signals=[
            SignalEvaluation(signal="large_incoming_transaction", status="MATCH", weight=0.2),
            SignalEvaluation(signal="verified_supplier_relationships", status="UNKNOWN", weight=0.6),
        ],
    )

    evidence = find_decision_critical_evidence([comparison])

    assert "verified supplier relationships" in evidence.question.lower()

