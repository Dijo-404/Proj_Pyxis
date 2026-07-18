from datetime import datetime, timezone

from pydantic import BaseModel, Field

from app.schemas.anomaly import AnomalyAssessment, TriggeredRule
from app.schemas.evidence import DecisionCriticalEvidence, EvidenceComparison
from app.schemas.financial_twin import FinancialTwin
from app.schemas.scenario import GemmaInvestigation, Scenario


class RiskCaseResponse(BaseModel):
    case_id: str
    customer_id: str
    trigger_transaction_id: str
    status: str = "OPEN"
    initial_anomaly_score: int = Field(ge=0, le=100)
    current_risk_score: int = Field(ge=0, le=100)
    risk_level: str
    financial_twin: FinancialTwin
    anomaly_assessment: AnomalyAssessment
    gemma_investigation: GemmaInvestigation
    scenarios: list[Scenario]
    evidence_comparisons: list[EvidenceComparison]
    decision_critical_evidence: DecisionCriticalEvidence
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def demo_case(cls) -> "RiskCaseResponse":
        twin = FinancialTwin.demo_baseline("CUST-001")
        anomaly = AnomalyAssessment(score=89, risk_level="HIGH", deviation_level="SEVERE", triggered_rules=[TriggeredRule(rule_id="amount_above_customer_p95", severity="HIGH", description="Amount exceeds baseline.")])
        scenario = Scenario(scenario_id="SCN-DEMO", category="SUSPICIOUS", name="Transaction Layering", description="Rapid redistribution of unusual funds.", expected_signals=[{"signal": "large_incoming_transaction", "weight": 1}])
        investigation = GemmaInvestigation(case_summary="Review required.", scenarios=[scenario], recommended_actions=["Verify suppliers"])
        comparison = EvidenceComparison(scenario_id="SCN-DEMO", match_score=0.84)
        critical = DecisionCriticalEvidence(question="Are the beneficiaries verified supplier relationships?", why_it_matters="This separates legitimate supplier settlement from layering.", recommended_action="Request supplier records.")
        return cls(case_id="CASE-DEMO", customer_id="CUST-001", trigger_transaction_id="TXN-DEMO", initial_anomaly_score=89, current_risk_score=84, risk_level="HIGH", financial_twin=twin, anomaly_assessment=anomaly, gemma_investigation=investigation, scenarios=[scenario], evidence_comparisons=[comparison], decision_critical_evidence=critical)

