from pydantic import BaseModel, Field


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

