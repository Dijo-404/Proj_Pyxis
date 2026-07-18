# Backend Member 2 — Compliance Investigation and Case Management

This implementation consumes a strict risk-case JSON document and owns the complete
compliance workflow after financial-risk analysis. It does not import or call Member
1's intelligence code.

## Handoff boundary

Member 2 accepts only this shape at `POST /api/v1/cases/import`:

```json
{
  "case_id": "CASE-001",
  "customer_id": "CUST-001",
  "risk_score": 89,
  "risk_level": "HIGH",
  "anomalies": ["Rapid redistribution"],
  "scenarios": [
    {
      "scenario_id": "SCN-LAYERING-001",
      "name": "Transaction Layering",
      "category": "SUSPICIOUS",
      "match_score": 84,
      "description": "Incoming funds were rapidly redistributed."
    }
  ],
  "supporting_evidence": ["Five new beneficiaries"],
  "contradicting_evidence": ["A matching invoice exists"],
  "missing_evidence": ["Supplier relationships are unverified"],
  "decision_critical_evidence": {
    "question": "Are the receiving accounts verified suppliers?",
    "why_it_matters": "Verification separates the leading scenarios.",
    "recommended_action": "Request supplier relationship records."
  },
  "recommended_actions": ["Verify beneficiary relationships"]
}
```

Unknown fields, invalid enums, unsafe IDs, scores outside `0..100`, and partially
specified decision-critical evidence are rejected. An empty
`decision_critical_evidence` object is accepted for compatibility with cases where
Member 1 has not identified a differentiating question.

Imported evidence is persisted as `UNVERIFIED`; missing evidence is persisted as
`MISSING`. Only reviewer APIs can verify evidence or set a final case disposition.

## API

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/cases/import` | Import a Member 1 risk case |
| `GET` | `/api/v1/cases` | Filtered, prioritized case queue |
| `GET` | `/api/v1/cases/{case_id}` | Complete case investigation |
| `PATCH` | `/api/v1/cases/{case_id}` | Administrative status/priority update |
| `GET` | `/api/v1/cases/{case_id}/evidence` | List case evidence |
| `POST` | `/api/v1/cases/{case_id}/evidence` | Add reviewer evidence |
| `PATCH` | `/api/v1/evidence/{evidence_id}/verify` | Verify or contradict evidence |
| `POST` | `/api/v1/documents/upload` | Upload and locally parse a document |
| `GET` | `/api/v1/cases/{case_id}/documents` | List case documents |
| `POST` | `/api/v1/documents/{document_id}/verify` | Verify or reject a document |
| `POST` | `/api/v1/cases/{case_id}/ask-gemma` | Ask local Gemma about one case |
| `POST` | `/api/v1/cases/{case_id}/review` | Record a human review action |
| `GET` | `/api/v1/cases/{case_id}/reviews` | List human review history |
| `GET` | `/api/v1/cases/{case_id}/audit` | Read the append-only case audit trail |
| `POST` | `/api/v1/reports/{case_id}/generate` | Generate local HTML/PDF report |
| `GET` | `/api/v1/reports/{case_id}` | Retrieve the latest report record |

Application errors use a stable envelope:

```json
{
  "error": {
    "code": "CASE_ALREADY_EXISTS",
    "message": "case 'CASE-001' has already been imported"
  }
}
```

## Review workflow

The review endpoint maps actions to case states:

| Action | Resulting status |
|---|---|
| `CLEAR` | `CLEARED` |
| `REQUEST_MORE_EVIDENCE` | `AWAITING_EVIDENCE` |
| `ESCALATE` | `ESCALATED` |
| `MARK_SUSPICIOUS` | `SUSPICIOUS` |
| `CLOSE` | `CLOSED` |

`CLOSE` requires a prior `CLEARED` or `SUSPICIOUS` disposition. Final dispositions
cannot be set through the general case update endpoint.

## Documents

Supported uploads are `.txt`, `.md`, `.csv`, `.json`, and `.pdf`. Files are:

1. size-limited and written under generated names,
2. parsed locally with PyMuPDF for PDFs,
3. sent through local Tesseract OCR only when a PDF has no text layer,
4. deterministically inspected for invoice, amount, and date candidates,
5. chunked with source IDs for later retrieval,
6. added as unverified document evidence.

Neither parsing nor indexing transmits document content outside the host.

## Local Gemma

`PYXIS_GEMMA_BASE_URL` must use `localhost` or an explicit private/loopback IP.
The HTTP client ignores proxy environment variables and refuses redirects. The case
assistant receives only the selected case context and must return schema-validated
JSON. Invalid or unavailable model output returns `503 LOCAL_AI_UNAVAILABLE`.

The configured server must expose an OpenAI-compatible endpoint at:

```text
POST {PYXIS_GEMMA_BASE_URL}/chat/completions
```

## Database and migrations

SQLite is the only supported database. The file location is configured with
`PYXIS_DATABASE_PATH` and defaults to `./pyxis.db`.

```bash
alembic upgrade head
```

Production should set `PYXIS_DATABASE_AUTO_CREATE=false` and apply migrations before
starting the API.

## Run and verify

```bash
python -m pip install -e '.[documents,reports,dev]'
alembic upgrade head
uvicorn backend.app.main:app --reload
python scripts/run_demo.py
pytest backend/tests
```

The demo imports [the synthetic mock risk case](../sandbox/mock_risk_case.json). A
local Gemma runtime is needed only for Ask Gemma and report narrative generation.

Authentication and role mapping are intentionally outside the supplied Member 2
assignment. Until the authentication module is integrated, reviewer IDs in sandbox
requests are asserted identities and must not be treated as production authentication.
