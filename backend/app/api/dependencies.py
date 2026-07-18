"""FastAPI dependencies shared by versioned routes."""

from typing import Annotated

from fastapi import Depends

from backend.app.core.config import Settings, get_settings

SettingsDependency = Annotated[Settings, Depends(get_settings)]
