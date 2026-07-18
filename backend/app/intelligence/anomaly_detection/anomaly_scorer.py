from backend.app.intelligence.anomaly_detection.rule_engine import evaluate_rules
from backend.app.intelligence.anomaly_detection.statistical_detector import calculate_features
from backend.app.schemas.anomaly import AnomalyAssessment
from backend.app.schemas.financial_twin import FinancialTwin
from backend.app.schemas.transaction import TransactionInput


RULE_WEIGHTS = {
    "amount_above_customer_p95": 35,
    "new_beneficiary": 18,
    "new_country": 18,
    "high_hourly_velocity": 20,
    "unusual_time": 8,
}


def score_transaction(transaction: TransactionInput, twin: FinancialTwin, hourly_velocity: int = 1) -> AnomalyAssessment:
    rules = evaluate_rules(transaction, twin, hourly_velocity)
    score = min(100, sum(RULE_WEIGHTS.get(rule.rule_id, 5) for rule in rules))
    if score >= 75:
        risk_level = "HIGH"
        deviation_level = "SEVERE"
    elif score >= 45:
        risk_level = "MEDIUM"
        deviation_level = "ELEVATED"
    else:
        risk_level = "LOW"
        deviation_level = "NORMAL"
    return AnomalyAssessment(score=score, risk_level=risk_level, deviation_level=deviation_level, features=calculate_features(transaction, twin, hourly_velocity), triggered_rules=rules)

