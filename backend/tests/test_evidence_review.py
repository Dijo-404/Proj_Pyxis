"""Evidence verification and reviewer disposition workflow tests."""

from fastapi.testclient import TestClient


def test_manages_evidence_and_review_transitions(
    client: TestClient, risk_case_payload: dict[str, object]
) -> None:
    client.post("/api/v1/cases/import", json=risk_case_payload)
    created = client.post(
        "/api/v1/cases/CASE-001/evidence",
        json={
            "scenario_id": "SCN-BUSINESS-001",
            "evidence_type": "REVIEWER",
            "description": "Supplier A registration record was uploaded.",
            "source_reference": "reviewer-note-1",
            "confidence": 0.8,
            "submitted_by": "OFFICER-12",
        },
    )
    assert created.status_code == 201
    evidence_id = created.json()["evidence_id"]
    assert created.json()["status"] == "UNVERIFIED"

    verified = client.patch(
        f"/api/v1/evidence/{evidence_id}/verify",
        json={
            "status": "VERIFIED",
            "reviewer_id": "OFFICER-12",
            "reason": "Registration was checked against the submitted record.",
        },
    )
    assert verified.status_code == 200
    assert verified.json()["status"] == "VERIFIED"

    request_more = client.post(
        "/api/v1/cases/CASE-001/review",
        json={
            "reviewer_id": "OFFICER-12",
            "action": "REQUEST_MORE_EVIDENCE",
            "reason": "Four supplier relationships remain unresolved.",
        },
    )
    assert request_more.status_code == 201
    assert request_more.json()["resulting_status"] == "AWAITING_EVIDENCE"

    suspicious = client.post(
        "/api/v1/cases/CASE-001/review",
        json={
            "reviewer_id": "OFFICER-12",
            "action": "MARK_SUSPICIOUS",
            "reason": "Unresolved beneficiaries exhibit pass-through behavior.",
        },
    )
    assert suspicious.status_code == 201
    assert suspicious.json()["resulting_status"] == "SUSPICIOUS"

    closed = client.post(
        "/api/v1/cases/CASE-001/review",
        json={
            "reviewer_id": "OFFICER-12",
            "action": "CLOSE",
            "reason": "Final disposition and escalation records are complete.",
        },
    )
    assert closed.status_code == 201
    assert closed.json()["resulting_status"] == "CLOSED"

    case = client.get("/api/v1/cases/CASE-001").json()
    assert case["status"] == "CLOSED"
    assert len(client.get("/api/v1/cases/CASE-001/reviews").json()) == 3


def test_cannot_close_without_disposition(
    client: TestClient, risk_case_payload: dict[str, object]
) -> None:
    client.post("/api/v1/cases/import", json=risk_case_payload)
    response = client.post(
        "/api/v1/cases/CASE-001/review",
        json={
            "reviewer_id": "OFFICER-12",
            "action": "CLOSE",
            "reason": "Premature close attempt.",
        },
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "FINAL_DISPOSITION_REQUIRED"
