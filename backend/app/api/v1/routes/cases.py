from fastapi import APIRouter

from backend.app.core.errors import not_found
from backend.app.db.session import risk_case_service
from backend.app.schemas.common import ApiResponse
from backend.app.schemas.evidence import EvidenceComparison
from backend.app.schemas.risk_case import RiskCaseResponse
from backend.app.schemas.scenario import Scenario

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("/{case_id}", response_model=ApiResponse[RiskCaseResponse])
def get_case(case_id: str) -> ApiResponse[RiskCaseResponse]:
    risk_case = risk_case_service.get_case(case_id)
    if risk_case is None:
        raise not_found("Risk case not found")
    return ApiResponse(data=risk_case)


@router.post("/{case_id}/investigate", response_model=ApiResponse[RiskCaseResponse])
def investigate_case(case_id: str) -> ApiResponse[RiskCaseResponse]:
    risk_case = risk_case_service.investigate_case(case_id)
    if risk_case is None:
        raise not_found("Risk case not found")
    return ApiResponse(data=risk_case)


@router.get("/{case_id}/scenarios", response_model=ApiResponse[list[Scenario]])
def get_case_scenarios(case_id: str) -> ApiResponse[list[Scenario]]:
    risk_case = risk_case_service.get_case(case_id)
    if risk_case is None:
        raise not_found("Risk case not found")
    return ApiResponse(data=risk_case.scenarios)


@router.get("/{case_id}/evidence", response_model=ApiResponse[list[EvidenceComparison]])
def get_case_evidence(case_id: str) -> ApiResponse[list[EvidenceComparison]]:
    risk_case = risk_case_service.get_case(case_id)
    if risk_case is None:
        raise not_found("Risk case not found")
    return ApiResponse(data=risk_case.evidence_comparisons)
