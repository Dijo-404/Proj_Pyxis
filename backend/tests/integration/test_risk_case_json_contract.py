from app.schemas.risk_case import RiskCaseResponse


def test_risk_case_contract_requires_core_case_fields():
    case = RiskCaseResponse.demo_case()

    assert case.case_id == "CASE-DEMO"
    assert case.current_risk_score >= case.initial_anomaly_score - 20
    assert case.gemma_investigation.scenarios
