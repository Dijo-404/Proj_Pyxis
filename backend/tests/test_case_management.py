"""Member 2 case import, filtering, update, and audit behavior."""

from copy import deepcopy

from fastapi.testclient import TestClient


def test_imports_and_retrieves_strict_risk_case(
    client: TestClient, risk_case_payload: dict[str, object]
) -> None:
    response = client.post("/api/v1/cases/import", json=risk_case_payload)

    assert response.status_code == 201
    imported = response.json()
    assert imported["case_id"] == "CASE-001"
    assert imported["status"] == "OPEN"
    assert imported["priority"] == 2
    assert len(imported["scenarios"]) == 2
    assert {item["evidence_type"] for item in imported["evidence"]} == {
        "SUPPORTING",
        "CONTRADICTING",
        "MISSING",
    }

    detail = client.get("/api/v1/cases/CASE-001")
    assert detail.status_code == 200
    assert detail.json() == imported


def test_rejects_duplicate_and_unknown_import_fields(
    client: TestClient, risk_case_payload: dict[str, object]
) -> None:
    assert client.post("/api/v1/cases/import", json=risk_case_payload).status_code == 201

    duplicate = client.post("/api/v1/cases/import", json=risk_case_payload)
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "CASE_ALREADY_EXISTS"

    invalid = deepcopy(risk_case_payload)
    invalid["unexpected_customer_dump"] = {"secret": True}
    rejected = client.post("/api/v1/cases/import", json=invalid)
    assert rejected.status_code == 422


def test_accepts_empty_but_rejects_partial_decision_critical_evidence(
    client: TestClient, risk_case_payload: dict[str, object]
) -> None:
    risk_case_payload["decision_critical_evidence"] = {}
    accepted = client.post("/api/v1/cases/import", json=risk_case_payload)
    assert accepted.status_code == 201
    assert accepted.json()["decision_critical_evidence"] == {}

    partial = deepcopy(risk_case_payload)
    partial["case_id"] = "CASE-002"
    partial["decision_critical_evidence"] = {"question": "Is the invoice verified?"}
    rejected = client.post("/api/v1/cases/import", json=partial)
    assert rejected.status_code == 422


def test_filters_prioritizes_and_updates_case(
    client: TestClient, risk_case_payload: dict[str, object]
) -> None:
    client.post("/api/v1/cases/import", json=risk_case_payload)
    update = client.patch(
        "/api/v1/cases/CASE-001",
        json={
            "status": "UNDER_REVIEW",
            "priority": 1,
            "actor_id": "OFFICER-12",
            "reason": "High-value case accepted for review.",
        },
    )
    assert update.status_code == 200
    assert update.json()["status"] == "UNDER_REVIEW"
    assert update.json()["priority"] == 1

    queue = client.get(
        "/api/v1/cases",
        params={"status": "UNDER_REVIEW", "minimum_risk_score": 80},
    )
    assert queue.status_code == 200
    assert [item["case_id"] for item in queue.json()] == ["CASE-001"]

    audit = client.get("/api/v1/cases/CASE-001/audit").json()
    assert [event["action"] for event in audit] == ["CASE_IMPORTED", "CASE_UPDATED"]


def test_terminal_status_requires_review_api(
    client: TestClient, risk_case_payload: dict[str, object]
) -> None:
    client.post("/api/v1/cases/import", json=risk_case_payload)
    response = client.patch(
        "/api/v1/cases/CASE-001",
        json={
            "status": "SUSPICIOUS",
            "actor_id": "OFFICER-12",
            "reason": "Attempt to bypass review workflow.",
        },
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "REVIEW_ACTION_REQUIRED"
