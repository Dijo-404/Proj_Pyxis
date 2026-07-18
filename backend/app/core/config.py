"""Environment-backed application configuration."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded only from local environment sources."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="PYXIS_",
        extra="ignore",
    )

    app_name: str = "Pyxis Compliance API"
    app_version: str = "0.1.0"
    environment: str = "development"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./pyxis.db"
    log_level: str = "INFO"
    gemma_provider: str = "transformers"
    gemma_model_path: str = "./models/gemma"
    allow_external_ai: Literal[False] = False


@lru_cache
def get_settings() -> Settings:
    """Return one immutable-by-convention settings instance per process."""
    return Settings()
