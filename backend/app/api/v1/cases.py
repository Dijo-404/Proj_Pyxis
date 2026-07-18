"""Risk-case import, queue, retrieval, and administrative update endpoints."""

from typing import Annotated

from fastapi import APIRouter, Query, status

from backend.app.api.dependencies import SessionDependency
from backend.app.schemas.case import (
    RiskCaseImport,
    RiskCaseRead,
    RiskCaseSummary,
    RiskCaseUpdate,
)
from backend.app.schemas.common import CaseStatus, Identifier, RiskLevel
from backend.app.services.case_service import CaseService

router = APIRouter(prefix="/cases", tags=["cases"])


@router.post("/import", response_model=RiskCaseRead, status_code=status.HTTP_201_CREATED)
def import_case(payload: RiskCaseImport, session: SessionDependency) -> RiskCaseRead:
    risk_case = CaseService(session).import_case(payload)
    return RiskCaseRead.model_validate(risk_case)


@router.get("", response_model=list[RiskCaseSummary])
def list_cases(
    session: SessionDependency,
    case_status: CaseStatus | None = Query(default=None, alias="status"),
    risk_level: RiskLevel | None = None,
    customer_id: Identifier | None = None,
    minimum_risk_score: Annotated[float | None, Query(ge=0, le=100)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
) -> list[RiskCaseSummary]:
    cases = CaseService(session).list_cases(
        status=case_status,
        risk_level=risk_level,
        customer_id=customer_id,
        minimum_risk_score=minimum_risk_score,
        offset=offset,
        limit=limit,
    )
    return [RiskCaseSummary.model_validate(risk_case) for risk_case in cases]


@router.get("/{case_id}", response_model=RiskCaseRead)
def get_case(case_id: Identifier, session: SessionDependency) -> RiskCaseRead:
    return RiskCaseRead.model_validate(CaseService(session).get_case(case_id))


@router.patch("/{case_id}", response_model=RiskCaseRead)
def update_case(
    case_id: Identifier, payload: RiskCaseUpdate, session: SessionDependency
) -> RiskCaseRead:
    return RiskCaseRead.model_validate(CaseService(session).update_case(case_id, payload))
