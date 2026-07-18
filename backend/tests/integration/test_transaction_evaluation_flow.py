from fastapi.testclient import TestClient

from backend.app.main import app


def test_transaction_evaluation_creates_risk_case_json():
    client = TestClient(app)
    payload = {
        "transaction": {
            "transaction_id": "TXN-100234",
            "customer_id": "CUST-001",
            "source_account": "ACC-100",
            "destination_account": "ACC-750",
            "amount": 1200000,
            "currency": "INR",
            "transaction_type": "BANK_TRANSFER",
            "direction": "CREDIT",
            "timestamp": "2026-07-18T10:02:34",
            "channel": "MOBILE_BANKING",
            "country": "UAE",
            "beneficiary_id": "BEN-450",
            "device_id": "DEV-20",
            "status": "SUCCESS",
        },
        "customer_profile": {
            "customer_id": "CUST-001",
            "customer_type": "BUSINESS",
            "declared_business": "Textile Retail",
            "declared_monthly_turnover": 700000,
            "country": "India",
            "account_age_months": 36,
            "kyc_status": "VERIFIED",
        },
    }

    response = client.post("/api/v1/transactions/evaluate", json=payload)

    assert response.status_code == 201
    body = response.json()["data"]
    assert body["case_id"].startswith("CASE-")
    assert body["risk_level"] == "HIGH"
    assert body["scenarios"]
    assert body["evidence_comparisons"]
    assert body["decision_critical_evidence"]["question"]

