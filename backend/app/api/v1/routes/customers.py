from fastapi import APIRouter

from backend.app.core.errors import not_found
from backend.app.db.session import risk_case_service
from backend.app.schemas.common import ApiResponse
from backend.app.schemas.customer import CustomerProfile
from backend.app.schemas.financial_twin import FinancialTwin


router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("/{customer_id}/financial-twin", response_model=ApiResponse[FinancialTwin])
def get_financial_twin(customer_id: str) -> ApiResponse[FinancialTwin]:
    twin = risk_case_service.get_twin(customer_id)
    if twin is None:
        raise not_found("Financial twin not found")
    return ApiResponse(data=twin)


@router.post("/{customer_id}/financial-twin/rebuild", response_model=ApiResponse[FinancialTwin])
def rebuild_financial_twin(customer_id: str, customer: CustomerProfile) -> ApiResponse[FinancialTwin]:
    if customer.customer_id != customer_id:
        raise ValueError("Path customer_id must match body customer_id")
    return ApiResponse(data=risk_case_service.rebuild_twin(customer))

