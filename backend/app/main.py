"""FastAPI application factory for the local Pyxis API."""

from fastapi import FastAPI

from backend.app.api.v1.router import api_router
from backend.app.core.config import get_settings


def create_app() -> FastAPI:
    """Create the API without performing database or model side effects."""
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url=None,
    )
    application.include_router(api_router, prefix=settings.api_v1_prefix)

    @application.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": settings.app_name}

    return application


app = create_app()
