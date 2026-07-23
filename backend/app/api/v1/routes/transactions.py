"""Live transaction evaluation: runs the real twin/anomaly/scenario/evidence pipeline
and persists the result as a reviewable, reportable DB-backed case.
"""

from time import perf_counter

from fastapi import APIRouter, status

from backend.app.api.dependencies import SessionDependency, SettingsDependency
from backend.app.db.session import risk_case_service, transaction_service
from backend.app.intelligence.gemma.provider import describe_investigation_provider
from backend.app.schemas.case import RiskCaseRead
from backend.app.schemas.common import ApiResponse
from backend.app.schemas.transaction import TransactionEvaluateRequest, TransactionInput
from backend.app.services.case_service import CaseService
from backend.app.services.risk_case_import_builder import build_risk_case_import

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post(
    "/evaluate", response_model=ApiResponse[RiskCaseRead], status_code=status.HTTP_201_CREATED
)
def evaluate_transaction(
    request: TransactionEvaluateRequest, session: SessionDependency, settings: SettingsDependency
) -> ApiResponse[RiskCaseRead]:
    started = perf_counter()
    risk_case = risk_case_service.evaluate_transaction(request)
    elapsed_ms = max(1, round((perf_counter() - started) * 1000))

    history = risk_case_service.transactions.list_for_customer(request.customer_profile.customer_id)
    model_name, runtime_label, boundary_held = describe_investigation_provider(settings)
    payload = build_risk_case_import(
        risk_case=risk_case,
        customer=request.customer_profile,
        transaction=request.transaction,
        history=history,
        total_duration_ms=elapsed_ms,
        model_name=model_name,
        runtime_label=runtime_label,
        boundary_held=boundary_held,
    )
    imported = CaseService(session).import_case(payload)
    return ApiResponse(data=RiskCaseRead.model_validate(imported))


@router.post("/import", response_model=ApiResponse[dict[str, int]])
def import_transactions(transactions: list[TransactionInput]) -> ApiResponse[dict[str, int]]:
    count = transaction_service.import_transactions(transactions)
    return ApiResponse(data={"imported": count})
