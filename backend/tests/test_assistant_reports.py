"""Case-scoped assistant auditing and local report generation tests."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from report_engine.export import export_pdf


def test_asks_case_scoped_assistant_and_audits_query(
    client: TestClient, risk_case_payload: dict[str, object]
) -> None:
    client.post("/api/v1/cases/import", json=risk_case_payload)
    response = client.post(
        "/api/v1/cases/CASE-001/ask-gemma",
        json={
            "reviewer_id": "OFFICER-12",
            "question": "Why does this case require review?",
        },
    )
    assert response.status_code == 200
    assert response.json()["evidence_references"] == ["CASE-001-EVD-001"]

    audit = client.get("/api/v1/cases/CASE-001/audit").json()
    query_event = next(event for event in audit if event["action"] == "GEMMA_ASSISTANT_QUERIED")
    assert len(query_event["metadata"]["question_sha256"]) == 64


def test_generates_escaped_html_report_and_retrieves_latest(
    client: TestClient, risk_case_payload: dict[str, object]
) -> None:
    risk_case_payload["supporting_evidence"] = ["<script>alert('unsafe')</script>"]
    client.post("/api/v1/cases/import", json=risk_case_payload)

    generated = client.post(
        "/api/v1/reports/CASE-001/generate",
        json={"generated_by": "OFFICER-12", "include_pdf": False},
    )
    assert generated.status_code == 201, generated.text
    report = generated.json()
    html_path = Path(report["html_path"])
    assert html_path.exists()
    html = html_path.read_text(encoding="utf-8")
    assert "<script>alert('unsafe')</script>" not in html
    assert "&lt;script&gt;" in html
    assert report["pdf_path"] is None

    latest = client.get("/api/v1/reports/CASE-001")
    assert latest.status_code == 200
    assert latest.json()["report_id"] == report["report_id"]


def test_exports_pdf_when_local_renderer_is_installed(tmp_path: Path) -> None:
    pytest.importorskip("weasyprint")
    destination = tmp_path / "report.pdf"

    export_pdf("<html><body><h1>Local report</h1></body></html>", destination)

    assert destination.read_bytes().startswith(b"%PDF")


def test_report_api_generates_pdf_when_renderer_is_installed(
    client: TestClient, risk_case_payload: dict[str, object]
) -> None:
    pytest.importorskip("weasyprint")
    client.post("/api/v1/cases/import", json=risk_case_payload)

    generated = client.post(
        "/api/v1/reports/CASE-001/generate",
        json={"generated_by": "OFFICER-12", "include_pdf": True},
    )

    assert generated.status_code == 201, generated.text
    assert Path(generated.json()["pdf_path"]).read_bytes().startswith(b"%PDF")
