"""Transaction ingestion and lookup endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/transactions", tags=["transactions"])
