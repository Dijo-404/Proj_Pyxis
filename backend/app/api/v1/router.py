"""Composition root for version 1 API routes."""

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

api_router = APIRouter()
api_router.include_router(transactions.router)
api_router.include_router(customers.router)
api_router.include_router(cases.router)
api_router.include_router(investigations.router)
api_router.include_router(documents.router)
api_router.include_router(reports.router)
api_router.include_router(websocket.router)
