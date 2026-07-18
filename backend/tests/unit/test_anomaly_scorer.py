from datetime import datetime

from app.intelligence.anomaly_detection.anomaly_scorer import score_transaction
from app.schemas.financial_twin import FinancialTwin
from app.schemas.transaction import TransactionInput


def test_score_transaction_flags_large_new_foreign_beneficiary():
    twin = FinancialTwin.demo_baseline("C1")
    transaction = TransactionInput(transaction_id="T9", customer_id="C1", source_account="A1", destination_account="A9", amount=1200000, currency="INR", transaction_type="BANK_TRANSFER", direction="CREDIT", timestamp=datetime(2026, 7, 18, 10), channel="MOBILE_BANKING", country="UAE", beneficiary_id="B9", device_id="D1", status="SUCCESS")

    assessment = score_transaction(transaction, twin, hourly_velocity=6)

    assert assessment.score >= 80
    assert assessment.risk_level == "HIGH"
    assert {"amount_above_customer_p95", "new_beneficiary", "new_country", "high_hourly_velocity"}.issubset({rule.rule_id for rule in assessment.triggered_rules})

