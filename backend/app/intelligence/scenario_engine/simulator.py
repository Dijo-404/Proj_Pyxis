from backend.app.intelligence.scenario_engine.match_scorer import calculate_match_score
from backend.app.intelligence.scenario_engine.signal_evaluator import evaluate_signal
from backend.app.schemas.anomaly import AnomalyAssessment
from backend.app.schemas.evidence import EvidenceComparison
from backend.app.schemas.scenario import Scenario
from backend.app.schemas.transaction import TransactionInput


def simulate_scenario(
    scenario: Scenario, transaction: TransactionInput, anomaly: AnomalyAssessment
) -> EvidenceComparison:
    signals = [
        evaluate_signal(signal, transaction, anomaly) for signal in scenario.expected_signals
    ]
    return EvidenceComparison(
        scenario_id=scenario.scenario_id,
        match_score=calculate_match_score(signals),
        signals=signals,
        supporting_evidence=[
            signal.signal for signal in signals if signal.status in {"MATCH", "PARTIAL"}
        ],
        contradicting_evidence=[
            signal.signal for signal in signals if signal.status == "CONTRADICT"
        ],
        unknown_evidence=[signal.signal for signal in signals if signal.status == "UNKNOWN"],
    )
