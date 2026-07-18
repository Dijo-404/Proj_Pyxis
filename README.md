# Pyxis

Private Adaptive Financial Intelligence powered by Gemma.

Pyxis is a local-first financial compliance and risk-triage platform. It builds a
trusted behavioral profile for each customer, detects deviations, compares
legitimate and suspicious scenarios, identifies decision-critical evidence, and
keeps the final decision with a human reviewer.

## Repository layout

- `backend/` — FastAPI application and application-layer services.
- `intelligence/` — deterministic analytics and local Gemma orchestration.
- `data_pipeline/` — ingestion, normalization, validation, and synthetic data.
- `report_engine/` — deterministic HTML/PDF report rendering.
- `database/` — relational schema, seed data, and sample queries.
- `mobile_app/` — Flutter reviewer application.
- `docs/` — architecture and focused design documents.
- `tests/` — cross-component integration and end-to-end tests.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
cp .env.example .env
alembic upgrade head
uvicorn backend.app.main:app --reload
```

The API health check is available at `http://127.0.0.1:8000/health` and the
interactive API documentation at `http://127.0.0.1:8000/docs`.

Pyxis uses SQLite exclusively. The database file defaults to `./pyxis.db` and can be
moved with `PYXIS_DATABASE_PATH`; no external database service or driver is required.
Customer data and model prompts must remain inside the institution-controlled
deployment boundary.

## Current status

The [Member 2 compliance backend](docs/member-2-backend.md) is implemented, including
case import/management, evidence, documents, local case-scoped Gemma Q&A, human review,
audit trails, reports, migrations, and integration tests. Member 1 financial-risk
intelligence and the Flutter feature screens remain for subsequent implementation.
