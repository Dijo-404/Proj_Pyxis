"""Strict Member 1 to Member 2 risk-case boundary and case API contracts."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.app.schemas.common import (
    CaseStatus,
    Identifier,
    LongText,
    RiskLevel,
    ShortText,
)
from backend.app.schemas.evidence import EvidenceRead
from backend.app.schemas.scenario import ScenarioImport, ScenarioRead


class DecisionCriticalEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: ShortText | None = None
    why_it_matters: LongText | None = None
    recommended_action: ShortText | None = None

    @model_validator(mode="after")
    def require_complete_or_empty(self) -> "DecisionCriticalEvidence":
        supplied = (self.question, self.why_it_matters, self.recommended_action)
        if any(value is not None for value in supplied) and any(
            value is None for value in supplied
        ):
            raise ValueError("decision-critical evidence must be complete or empty")
        return self


class RiskCaseImport(BaseModel):
    """The sole JSON contract expected from Member 1."""

    model_config = ConfigDict(extra="forbid")

    case_id: Identifier
    customer_id: Identifier
    risk_score: float = Field(ge=0, le=100)
    risk_level: RiskLevel
    anomalies: list[ShortText] = Field(default_factory=list, max_length=200)
    scenarios: list[ScenarioImport] = Field(default_factory=list, max_length=50)
    supporting_evidence: list[LongText] = Field(default_factory=list, max_length=500)
    contradicting_evidence: list[LongText] = Field(default_factory=list, max_length=500)
    missing_evidence: list[LongText] = Field(default_factory=list, max_length=500)
    decision_critical_evidence: DecisionCriticalEvidence | None = None
    recommended_actions: list[ShortText] = Field(default_factory=list, max_length=100)


class RiskCaseUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: CaseStatus | None = None
    priority: int | None = Field(default=None, ge=1, le=5)
    actor_id: Identifier
    reason: LongText

    @model_validator(mode="after")
    def require_change(self) -> "RiskCaseUpdate":
        if self.status is None and self.priority is None:
            raise ValueError("status or priority must be provided")
        return self


class RiskCaseSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    case_id: Identifier
    customer_id: Identifier
    risk_score: float
    risk_level: RiskLevel
    status: CaseStatus
    priority: int
    created_at: datetime
    updated_at: datetime


class RiskCaseRead(RiskCaseSummary):
    anomalies: list[str]
    scenarios: list[ScenarioRead]
    evidence: list[EvidenceRead]
    decision_critical_evidence: dict[str, str] | None
    recommended_actions: list[str]
