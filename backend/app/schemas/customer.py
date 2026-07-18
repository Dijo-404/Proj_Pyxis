from pydantic import BaseModel, Field


class CustomerProfile(BaseModel):
    customer_id: str = Field(min_length=1)
    customer_type: str = Field(min_length=1)
    declared_business: str | None = None
    declared_monthly_turnover: float | None = Field(default=None, ge=0)
    country: str = Field(min_length=1)
    account_age_months: int = Field(ge=0)
    kyc_status: str = Field(min_length=1)

