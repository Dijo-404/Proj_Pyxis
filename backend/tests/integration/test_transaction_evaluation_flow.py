from fastapi.testclient import TestClient


def test_transaction_evaluation_persists_reviewable_case_json(client: TestClient):
    """Evaluating a transaction runs the real twin/anomaly/scenario/evidence pipeline and
    persists a reviewable, reportable DB-backed case — not a disconnected in-memory one.
    """
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
    assert body["decision_critical_evidence"]["question"]

    workspace_data = body["workspace_data"]
    assert workspace_data["scenario_evidence"]
    assert workspace_data["evidence_matrix"]
    assert workspace_data["financial_twin"]
    assert workspace_data["sandbox"]["stages"]
    assert workspace_data["sandbox"]["transactions"]

    # The persisted case is now retrievable and reviewable through the normal case API,
    # proving the two pipelines are actually unified rather than merely both present.
    get_response = client.get(f"/api/v1/cases/{body['case_id']}")
    assert get_response.status_code == 200
    assert get_response.json()["case_id"] == body["case_id"]
