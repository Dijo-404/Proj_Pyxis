from backend.app.intelligence.evidence_engine.critical_evidence import (
    find_decision_critical_evidence,
)
from backend.app.intelligence.evidence_engine.evidence_comparator import rank_comparisons
from backend.app.intelligence.scenario_engine.simulator import simulate_scenario
from backend.app.schemas.anomaly import AnomalyAssessment
from backend.app.schemas.evidence import DecisionCriticalEvidence, EvidenceComparison
from backend.app.schemas.scenario import Scenario
from backend.app.schemas.transaction import TransactionInput


class ScenarioService:
    def compare(
        self, scenarios: list[Scenario], transaction: TransactionInput, anomaly: AnomalyAssessment
    ) -> tuple[list[EvidenceComparison], DecisionCriticalEvidence]:
        comparisons = rank_comparisons(
            [simulate_scenario(scenario, transaction, anomaly) for scenario in scenarios]
        )
        return comparisons, find_decision_critical_evidence(comparisons)
