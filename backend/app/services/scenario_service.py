from app.intelligence.evidence_engine.critical_evidence import find_decision_critical_evidence
from app.intelligence.evidence_engine.evidence_comparator import rank_comparisons
from app.intelligence.scenario_engine.simulator import simulate_scenario
from app.schemas.anomaly import AnomalyAssessment
from app.schemas.evidence import DecisionCriticalEvidence, EvidenceComparison
from app.schemas.scenario import Scenario
from app.schemas.transaction import TransactionInput


class ScenarioService:
    def compare(self, scenarios: list[Scenario], transaction: TransactionInput, anomaly: AnomalyAssessment) -> tuple[list[EvidenceComparison], DecisionCriticalEvidence]:
        comparisons = rank_comparisons([simulate_scenario(scenario, transaction, anomaly) for scenario in scenarios])
        return comparisons, find_decision_critical_evidence(comparisons)

