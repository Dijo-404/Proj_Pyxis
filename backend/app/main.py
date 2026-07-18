"""FastAPI application factory for the local Pyxis API."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.app.api.v1.router import api_router
from backend.app.core.config import get_settings
from backend.app.core.database import initialize_database
from backend.app.core.logging import configure_logging
from backend.app.services.errors import ApplicationError


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Initialize only local infrastructure owned by this process."""
    settings = get_settings()
    configure_logging(settings.log_level)
    if settings.database_auto_create and settings.environment != "production":
        initialize_database()
    yield


def create_app() -> FastAPI:
    """Create the API without performing database or model side effects."""
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url=None,
        lifespan=lifespan,
    )
    application.include_router(api_router, prefix=settings.api_v1_prefix)

    @application.exception_handler(ApplicationError)
    async def application_error_handler(_: Request, error: ApplicationError) -> JSONResponse:
        return JSONResponse(
            status_code=error.status_code,
            content={"error": {"code": error.code, "message": error.message}},
        )

    @application.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": settings.app_name}

    return application


app = create_app()
