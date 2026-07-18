from backend.app.intelligence.financial_twin.trust_gate import should_learn_transaction
from backend.app.intelligence.financial_twin.twin_builder import build_financial_twin
from backend.app.schemas.customer import CustomerProfile
from backend.app.schemas.financial_twin import BehaviorProfile


def test_build_financial_twin_merges_behavior_and_business_profile():
    behavior = BehaviorProfile.for_empty_customer("C1")
    customer = CustomerProfile(
        customer_id="C1",
        customer_type="BUSINESS",
        declared_business="Textile Retail",
        declared_monthly_turnover=700000,
        country="India",
        account_age_months=36,
        kyc_status="VERIFIED",
    )

    twin = build_financial_twin(customer, behavior, version=2)

    assert twin.customer_id == "C1"
    assert twin.version == 2
    assert twin.business_profile.business_type == "Textile Retail"
    assert twin.business_profile.expected_monthly_turnover == 700000


def test_trust_gate_rejects_open_or_high_risk_activity():
    assert should_learn_transaction("CLEARED", 20) is True
    assert should_learn_transaction("OPEN", 20) is False
    assert should_learn_transaction("CLEARED", 80) is False
