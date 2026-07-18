"""Risk-case API contracts."""

from pydantic import BaseModel, ConfigDict, Field


class RiskCaseSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    customer_id: str
    trigger_transaction_id: str
    anomaly_score: float = Field(ge=0, le=100)
    status: str
