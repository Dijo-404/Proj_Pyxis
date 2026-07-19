"""Shared web/mobile workspace bootstrap contract tests."""

from fastapi.testclient import TestClient


def test_workspace_bootstrap_returns_persisted_cases_and_local_model(
    client: TestClient,
    risk_case_payload: dict[str, object],
) -> None:
    risk_case_payload.update(
        {
            "customer_name": "Synthetic Trading Co.",
            "customer_type": "BUSINESS",
            "business": "Industrial supplies",
            "trigger_transaction_id": "TXN-SYNTH-001",
            "trigger_summary": "Unusual payment to a newly observed beneficiary",
            "trigger_amount": "₹8,90,000",
            "assigned_to": "Test Reviewer",
            "location": "Pune, Maharashtra",
            "workspace_data": {"transaction_count": 1250, "anomaly_score": 93},
        }
    )
    imported = client.post("/api/v1/cases/import", json=risk_case_payload)
    assert imported.status_code == 201

    response = client.get("/api/v1/workspace/bootstrap")

    assert response.status_code == 200
    payload = response.json()
    assert "@" in payload["reviewer"]["email"]
    assert payload["model_runtime"]["provider"] == "ollama"
    assert payload["model_runtime"]["model"] == "gemma3:4b"
    assert payload["model_runtime"]["base_url"].endswith(":11434/v1")
    assert payload["model_runtime"]["local_only"] is True
    assert payload["dashboard"]["transactions_analyzed"] == 1250
    assert payload["dashboard"]["open_cases"] == 1
    assert payload["cases"][0]["customer_name"] == "Synthetic Trading Co."
    assert payload["cases"][0]["workspace_data"]["anomaly_score"] == 93
    assert payload["reports"] == []
