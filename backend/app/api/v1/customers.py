"""Customer profile and financial-twin endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/customers", tags=["customers"])
