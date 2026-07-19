"""Environment-backed application configuration."""

from functools import lru_cache
from pathlib import Path
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
    api_prefix: str = "/api/v1"
    api_v1_prefix: str = "/api/v1"
    database_path: Path = Path("./pyxis.db")
    database_auto_create: bool = True
    log_level: str = "INFO"
    gemma_provider: str = "ollama"
    gemma_model_path: str = "./models/gemma"
    gemma_base_url: str = "http://127.0.0.1:11434/v1"
    gemma_model: str = "gemma3:4b"
    gemma_timeout_seconds: float = 60.0
    local_gemma_enabled: bool = True
    cors_origins: list[str] = ["http://127.0.0.1:5173", "http://localhost:5173"]
    reviewer_id: str = "OFFICER-12"
    reviewer_name: str = "Priyan Kannaa"
    reviewer_email: str = "prie@gmail.com"
    reviewer_role: str = "Compliance Officer"
    document_storage_path: Path = Path("./data/documents")
    report_output_path: Path = Path("./reports")
    max_document_bytes: int = 20 * 1024 * 1024
    allow_external_ai: Literal[False] = False


@lru_cache
def get_settings() -> Settings:
    """Return one immutable-by-convention settings instance per process."""
    return Settings()
