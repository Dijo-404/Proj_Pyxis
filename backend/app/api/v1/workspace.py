"""Client bootstrap route shared by the web and React Native applications."""

from fastapi import APIRouter

from backend.app.api.dependencies import SessionDependency, SettingsDependency
from backend.app.schemas.workspace import WorkspaceBootstrap
from backend.app.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/workspace", tags=["workspace"])


@router.get("/bootstrap", response_model=WorkspaceBootstrap)
def get_workspace_bootstrap(
    session: SessionDependency,
    settings: SettingsDependency,
) -> WorkspaceBootstrap:
    return WorkspaceService(session, settings).bootstrap()
