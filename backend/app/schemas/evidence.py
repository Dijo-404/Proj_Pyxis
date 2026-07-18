from pydantic import BaseModel, Field


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

