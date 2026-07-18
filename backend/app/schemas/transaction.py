"""Transaction contracts shared by ingestion and risk simulation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from backend.app.schemas.customer import CustomerProfile


class TransactionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transaction_id: str = Field(min_length=1)
    customer_id: str = Field(min_length=1)
    source_account: str = Field(min_length=1)
    destination_account: str = Field(min_length=1)
    amount: float = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    transaction_type: str = Field(min_length=1)
    direction: str = Field(min_length=1)
    timestamp: datetime
    channel: str = Field(min_length=1)
    country: str = Field(min_length=1)
    beneficiary_id: str | None = None
    device_id: str | None = None
    status: str = Field(min_length=1)


class TransactionEvaluateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transaction: TransactionInput
    customer_profile: CustomerProfile
