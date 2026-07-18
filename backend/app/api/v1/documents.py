"""Local document upload and verification endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/documents", tags=["documents"])
