"""Transaction API contracts."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class TransactionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transaction_id: str
    customer_id: str
    source_account: str
    destination_account: str
    amount: Decimal
    currency: str
    transaction_type: str
    direction: str
    timestamp: datetime
    channel: str
    country: str
    beneficiary_id: str | None = None
    device_id: str | None = None
    status: str
