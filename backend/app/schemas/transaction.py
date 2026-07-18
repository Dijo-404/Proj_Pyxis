from datetime import datetime

from pydantic import BaseModel, Field


class TransactionInput(BaseModel):
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
    transaction: TransactionInput
    customer_profile: "CustomerProfile"


from backend.app.schemas.customer import CustomerProfile

TransactionEvaluateRequest.model_rebuild()

