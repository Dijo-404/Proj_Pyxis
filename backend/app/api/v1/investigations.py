"""Investigation, scenario, and reviewer-action endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/investigations", tags=["investigations"])
