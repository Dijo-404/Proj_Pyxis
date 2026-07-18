"""Scenario contracts for compliance storage and risk-engine simulation."""

from pydantic import BaseModel, ConfigDict, Field

from backend.app.schemas.common import Identifier, LongText, ScenarioCategory, ShortText


class ScenarioImport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_id: Identifier | None = None
    name: ShortText
    category: ScenarioCategory
    match_score: float = Field(ge=0, le=100)
    description: LongText | None = None


class ScenarioRead(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    scenario_id: Identifier
    case_id: Identifier
    name: str
    category: ScenarioCategory
    match_score: float
    description: str | None


class ExpectedSignal(BaseModel):
    signal: str = Field(min_length=1)
    weight: float = Field(gt=0)


class Scenario(BaseModel):
    scenario_id: str = Field(min_length=1)
    category: str = Field(pattern="^(LEGITIMATE|SUSPICIOUS|UNCERTAIN)$")
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    expected_signals: list[ExpectedSignal] = Field(min_length=1)


class GemmaInvestigation(BaseModel):
    case_summary: str
    scenarios: list[Scenario] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
