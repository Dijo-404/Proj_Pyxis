"""Composition root for the persistent API and recovered risk engine."""

from fastapi import APIRouter

from backend.app.api.v1 import (
    cases,
    customers,
    documents,
    investigations,
    reports,
    transactions,
    websocket,
)
from backend.app.api.v1.routes import (
    cases as risk_engine_cases,
)
from backend.app.api.v1.routes import (
    customers as risk_engine_customers,
)
from backend.app.api.v1.routes import (
    transactions as risk_engine_transactions,
)

api_router = APIRouter()
api_router.include_router(transactions.router)
api_router.include_router(customers.router)
api_router.include_router(cases.router)
api_router.include_router(investigations.router)
api_router.include_router(documents.router)
api_router.include_router(reports.router)
api_router.include_router(websocket.router)
# Preserve the recovered branch's non-conflicting public endpoints.
api_router.include_router(risk_engine_transactions.router, deprecated=True)
api_router.include_router(risk_engine_customers.router, deprecated=True)

risk_engine_router = APIRouter(prefix="/risk-engine")
risk_engine_router.include_router(risk_engine_transactions.router)
risk_engine_router.include_router(risk_engine_customers.router)
risk_engine_router.include_router(risk_engine_cases.router)
api_router.include_router(risk_engine_router)
