"""Local document parsing, evidence creation, and verification tests."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from document_processing.parser import parse_document


def test_uploads_parses_and_verifies_document(
    client: TestClient, risk_case_payload: dict[str, object]
) -> None:
    client.post("/api/v1/cases/import", json=risk_case_payload)
    response = client.post(
        "/api/v1/documents/upload",
        data={
            "case_id": "CASE-001",
            "customer_id": "CUST-001",
            "document_type": "INVOICE",
            "uploaded_by": "OFFICER-12",
        },
        files={
            "file": (
                "supplier-invoice.txt",
                b"Invoice INV-2026-99\nINR 120,000.00\nDate 2026-07-18",
                "text/plain",
            )
        },
    )
    assert response.status_code == 201, response.text
    document = response.json()
    assert document["verification_status"] == "UNVERIFIED"
    assert document["extracted_data"]["invoice_numbers"] == ["INV-2026-99"]
    assert document["sha256"]
    document_id = document["document_id"]

    listed = client.get("/api/v1/cases/CASE-001/documents")
    assert listed.status_code == 200
    assert [item["document_id"] for item in listed.json()] == [document_id]

    verified = client.post(
        f"/api/v1/documents/{document_id}/verify",
        json={
            "status": "VERIFIED",
            "reviewer_id": "OFFICER-12",
            "reason": "Invoice identifiers and amount were checked.",
        },
    )
    assert verified.status_code == 200
    assert verified.json()["verification_status"] == "VERIFIED"

    evidence = client.get("/api/v1/cases/CASE-001/evidence").json()
    document_evidence = next(item for item in evidence if item["source_reference"] == document_id)
    assert document_evidence["status"] == "VERIFIED"

    audit = client.get("/api/v1/cases/CASE-001/audit").json()
    assert "DOCUMENT_UPLOADED" in {event["action"] for event in audit}
    assert "DOCUMENT_VERIFIED" in {event["action"] for event in audit}
    assert document["extracted_data"]["parser_metadata"]["extension"] == ".txt"


def test_rejects_unsupported_document(
    client: TestClient, risk_case_payload: dict[str, object]
) -> None:
    client.post("/api/v1/cases/import", json=risk_case_payload)
    response = client.post(
        "/api/v1/documents/upload",
        data={
            "case_id": "CASE-001",
            "customer_id": "CUST-001",
            "document_type": "EXECUTABLE",
            "uploaded_by": "OFFICER-12",
        },
        files={"file": ("payload.exe", b"not allowed", "application/octet-stream")},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "UNSUPPORTED_DOCUMENT_TYPE"


def test_parses_text_layer_pdf_locally(tmp_path: Path) -> None:
    fitz = pytest.importorskip("fitz")
    pdf_path = tmp_path / "invoice.pdf"
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "Invoice INV-PDF-001 INR 2500")
    document.save(pdf_path)
    document.close()

    parsed = parse_document(pdf_path)

    assert "INV-PDF-001" in parsed.text
    assert parsed.metadata == {"extension": ".pdf", "pages": 1, "used_ocr": False}
