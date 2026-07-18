"""Scenario generation and scoring contracts."""

from pydantic import BaseModel, ConfigDict, Field


class ExpectedSignal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    signal: str
    weight: float = Field(gt=0, le=1)


class Scenario(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_id: str
    category: str
    name: str
    description: str
    expected_signals: list[ExpectedSignal]
