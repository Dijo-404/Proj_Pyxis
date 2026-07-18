"""Local compliance report generation and retrieval endpoints."""

from fastapi import APIRouter, status

from backend.app.api.dependencies import (
    ReportWriterDependency,
    SessionDependency,
    SettingsDependency,
)
from backend.app.schemas.common import Identifier
from backend.app.schemas.report import ReportRead, ReportRequest
from backend.app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post(
    "/{case_id}/generate",
    response_model=ReportRead,
    status_code=status.HTTP_201_CREATED,
)
async def generate_report(
    case_id: Identifier,
    payload: ReportRequest,
    session: SessionDependency,
    settings: SettingsDependency,
    writer: ReportWriterDependency,
) -> ReportRead:
    service = ReportService(
        session,
        writer=writer,
        output_path=settings.report_output_path,
    )
    return ReportRead.model_validate(await service.generate(case_id, payload))


@router.get("/{case_id}", response_model=ReportRead)
def get_latest_report(
    case_id: Identifier,
    session: SessionDependency,
    settings: SettingsDependency,
) -> ReportRead:
    service = ReportService(
        session,
        writer=None,
        output_path=settings.report_output_path,
    )
    return ReportRead.model_validate(service.latest_for_case(case_id))
