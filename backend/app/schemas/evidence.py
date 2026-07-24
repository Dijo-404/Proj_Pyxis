"""Evidence contracts for compliance storage and risk-engine evaluation."""

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


class SignalEvaluation(BaseModel):
    signal: str
    status: str = Field(pattern="^(MATCH|PARTIAL|UNKNOWN|CONTRADICT)$")
    weight: float = Field(ge=0)
    observed_value: str | None = None
    explanation: str | None = None


class EvidenceComparison(BaseModel):
    scenario_id: str
    match_score: float = Field(ge=0, le=1)
    signals: list[SignalEvaluation] = Field(default_factory=list)
    supporting_evidence: list[str] = Field(default_factory=list)
    contradicting_evidence: list[str] = Field(default_factory=list)
    unknown_evidence: list[str] = Field(default_factory=list)


class DecisionCriticalEvidence(BaseModel):
    question: str
    why_it_matters: str
    recommended_action: str


class CounterfactualStep(BaseModel):
    """One step of "if this evidence were verified, risk would change from X to Y"
    (spec §19). A scenario-based estimate, not a guaranteed prediction.
    """

    condition: str
    from_score: int = Field(ge=0, le=100, serialization_alias="from")
    to_score: int = Field(ge=0, le=100, serialization_alias="to")

    model_config = ConfigDict(populate_by_name=True)
