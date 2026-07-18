from pydantic import BaseModel, Field


class TriggeredRule(BaseModel):
    rule_id: str
    severity: str
    description: str


class AnomalyAssessment(BaseModel):
    score: int = Field(ge=0, le=100)
    risk_level: str
    deviation_level: str
    features: dict[str, float | int | bool | str | None] = Field(default_factory=dict)
    triggered_rules: list[TriggeredRule] = Field(default_factory=list)

