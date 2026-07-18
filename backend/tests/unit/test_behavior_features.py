from datetime import datetime

from app.intelligence.financial_twin.behavior_features import build_behavior_profile
from app.schemas.transaction import TransactionInput


def test_build_behavior_profile_summarizes_trusted_history():
    transactions = [
        TransactionInput(transaction_id="T1", customer_id="C1", source_account="A1", destination_account="A2", amount=100, currency="INR", transaction_type="BANK_TRANSFER", direction="DEBIT", timestamp=datetime(2026, 7, 1, 9), channel="MOBILE_BANKING", country="India", beneficiary_id="B1", device_id="D1", status="SUCCESS"),
        TransactionInput(transaction_id="T2", customer_id="C1", source_account="A1", destination_account="A3", amount=200, currency="INR", transaction_type="BANK_TRANSFER", direction="DEBIT", timestamp=datetime(2026, 7, 1, 10), channel="MOBILE_BANKING", country="India", beneficiary_id="B2", device_id="D1", status="SUCCESS"),
        TransactionInput(transaction_id="T3", customer_id="C1", source_account="A1", destination_account="A2", amount=300, currency="INR", transaction_type="BANK_TRANSFER", direction="DEBIT", timestamp=datetime(2026, 7, 2, 20), channel="BRANCH", country="UAE", beneficiary_id="B1", device_id="D2", status="SUCCESS"),
    ]

    profile = build_behavior_profile("C1", transactions)

    assert profile.amount_profile.median == 200
    assert profile.amount_profile.p95 >= 200
    assert profile.velocity_profile.average_transactions_per_day == 1.5
    assert profile.beneficiary_profile.known_beneficiaries == 2
    assert profile.geography_profile.common_countries == ["India", "UAE"]

