from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Pyxis Compliance API"
    app_version: str = "0.1.0"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    api_v1_prefix: str = "/api/v1"
    local_gemma_enabled: bool = True


settings = Settings()


def get_settings() -> Settings:
    return settings
