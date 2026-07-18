from fastapi import FastAPI

from backend.app.api.v1.router import api_router
from backend.app.core.config import settings


def create_app() -> FastAPI:
    application = FastAPI(title=settings.app_name, version=settings.app_version)

    @application.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok", "service": settings.app_name}

    application.include_router(api_router, prefix=settings.api_v1_prefix)
    return application


app = create_app()
