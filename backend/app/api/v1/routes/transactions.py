from fastapi import APIRouter, status

from app.db.session import risk_case_service, transaction_service
from app.schemas.common import ApiResponse
from app.schemas.risk_case import RiskCaseResponse
from app.schemas.transaction import TransactionEvaluateRequest, TransactionInput


router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/evaluate", response_model=ApiResponse[RiskCaseResponse], status_code=status.HTTP_201_CREATED)
def evaluate_transaction(request: TransactionEvaluateRequest) -> ApiResponse[RiskCaseResponse]:
    return ApiResponse(data=risk_case_service.evaluate_transaction(request))


@router.post("/import", response_model=ApiResponse[dict[str, int]])
def import_transactions(transactions: list[TransactionInput]) -> ApiResponse[dict[str, int]]:
    count = transaction_service.import_transactions(transactions)
    return ApiResponse(data={"imported": count})

