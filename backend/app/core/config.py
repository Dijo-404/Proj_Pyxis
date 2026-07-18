from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Pyxis Backend"
    api_prefix: str = "/api/v1"
    local_gemma_enabled: bool = True


settings = Settings()

