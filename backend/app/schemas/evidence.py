"""Evidence creation, verification, and response contracts."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from backend.app.schemas.common import (
    EvidenceStatus,
    EvidenceType,
    Identifier,
    LongText,
    ShortText,
)


class EvidenceCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_id: Identifier | None = None
    evidence_type: EvidenceType = EvidenceType.REVIEWER
    description: LongText
    source_reference: ShortText = "reviewer_submission"
    confidence: float = Field(default=0.5, ge=0, le=1)
    submitted_by: Identifier


class EvidenceVerification(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal[EvidenceStatus.VERIFIED, EvidenceStatus.CONTRADICTED]
    reviewer_id: Identifier
    reason: LongText


class EvidenceRead(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    evidence_id: Identifier
    case_id: Identifier
    scenario_id: Identifier | None
    evidence_type: EvidenceType
    description: str
    source_reference: str
    status: EvidenceStatus
    confidence: float
    submitted_by: str
    verification_reason: str | None
    verified_by: str | None
    verified_at: datetime | None
    created_at: datetime
