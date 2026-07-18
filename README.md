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
uvicorn backend.app.main:app --reload
```

The API health check is available at `http://127.0.0.1:8000/health` and the
interactive API documentation at `http://127.0.0.1:8000/docs`.

For PostgreSQL, start the local database with:

```bash
docker compose up -d postgres
```

The default development configuration uses SQLite so the API can start without
external infrastructure. Customer data and model prompts must remain inside the
institution-controlled deployment boundary.

## Current status

This repository contains the architecture-aligned base scaffold. Business logic,
database migrations, model-runtime integration, and feature screens are reserved
for subsequent implementation.
