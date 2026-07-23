"""Composition root for the unified compliance API.

`routes.transactions` runs the real analytics pipeline (twin/anomaly/scenario/evidence)
and persists the result via `CaseService`, so there is a single case pipeline instead of
a disconnected DB-backed one and an in-memory "risk-engine" one. `routes.customers`
exposes financial-twin inspection and is kept for the same reason.
"""

from fastapi import APIRouter

from backend.app.api.v1 import (
    cases,
    customers,
    documents,
    investigations,
    reports,
    transactions,
    websocket,
    workspace,
)
from backend.app.api.v1.routes import customers as risk_engine_customers
from backend.app.api.v1.routes import transactions as risk_engine_transactions

api_router = APIRouter()
api_router.include_router(transactions.router)
api_router.include_router(customers.router)
api_router.include_router(cases.router)
api_router.include_router(investigations.router)
api_router.include_router(documents.router)
api_router.include_router(reports.router)
api_router.include_router(websocket.router)
api_router.include_router(workspace.router)
api_router.include_router(risk_engine_transactions.router)
api_router.include_router(risk_engine_customers.router)
