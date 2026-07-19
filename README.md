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
- `web/` — Carbon-inspired React/Vite reviewer workspace.
- `mobile/pyxis/` — React Native reviewer application.
- `docs/` — architecture and focused design documents.
- `tests/` — cross-component integration and end-to-end tests.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
cp .env.example .env
alembic upgrade head
python scripts/seed_database.py
uvicorn backend.app.main:app --reload
```

The API health check is available at `http://127.0.0.1:8000/health` and the
interactive API documentation at `http://127.0.0.1:8000/docs`.

Pyxis uses SQLite exclusively. The database file defaults to `./pyxis.db` and can be
moved with `PYXIS_DATABASE_PATH`; no external database service or driver is required.
Customer data and model prompts must remain inside the institution-controlled
deployment boundary.

The seed command creates deterministic, fictional customers, transactions, scenarios,
evidence, counterfactuals, and sandbox traces in SQLite. It does not add a client-side
fixture fallback. Use `python scripts/seed_database.py --replace` only when you
intentionally want to replace the current development cases.

## Local model and clients

Pyxis uses the Ollama OpenAI-compatible endpoint with `gemma3:4b`:

```bash
ollama pull gemma3:4b
ollama serve
```

Start the website in a second terminal. Vite proxies `/api` to FastAPI on port 8000.

```bash
cd web
npm install
npm run dev
```

Start React Native Metro in a third terminal:

```bash
cd mobile/pyxis
npm install
npm start
# Then, with an emulator or device connected:
npm run android
```

The Android emulator calls FastAPI through `10.0.2.2:8000`; iOS Simulator uses
`127.0.0.1:8000`. Both clients load `/api/v1/workspace/bootstrap` and send case-scoped
questions to `/api/v1/cases/{case_id}/ask-gemma`.

## Current status

The FastAPI/SQLite backend, deterministic risk analytics, Ollama-powered case assistant,
React website, and React Native application share the same persistent workspace API.
Case import/management, evidence, human review, audit trails, reports, migrations, and
integration tests are implemented without an external database dependency.
