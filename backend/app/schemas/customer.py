"""Customer API contracts."""

from pydantic import BaseModel, ConfigDict


class CustomerSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: str
    customer_type: str
    country: str
    kyc_status: str
