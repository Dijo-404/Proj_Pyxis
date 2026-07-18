"""Human review workflow contracts."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from backend.app.schemas.common import CaseStatus, Identifier, LongText, ReviewAction


class ReviewCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reviewer_id: Identifier
    action: ReviewAction
    reason: LongText


class ReviewRead(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    review_id: Identifier
    case_id: Identifier
    reviewer_id: Identifier
    action: ReviewAction
    reason: str
    previous_status: CaseStatus
    resulting_status: CaseStatus
    created_at: datetime
