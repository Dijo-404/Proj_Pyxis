"""Strict scenario import and response contracts."""

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
