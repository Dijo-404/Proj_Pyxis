"""Customer contracts shared by the compliance API and risk engine."""

from pydantic import BaseModel, ConfigDict, Field


class CustomerProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: str = Field(min_length=1)
    customer_type: str = Field(min_length=1)
    declared_business: str | None = None
    declared_monthly_turnover: float | None = Field(default=None, ge=0)
    country: str = Field(min_length=1)
    account_age_months: int = Field(ge=0)
    kyc_status: str = Field(min_length=1)


class CustomerSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: str
    customer_type: str
    country: str
    kyc_status: str
