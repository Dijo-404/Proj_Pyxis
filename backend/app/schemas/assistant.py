"""Case-scoped local Gemma assistant contracts."""

from pydantic import BaseModel, ConfigDict, Field

from backend.app.schemas.common import Identifier, LongText


class CaseQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reviewer_id: Identifier
    question: LongText


class CaseAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: str = Field(min_length=1, max_length=20_000)
    evidence_references: list[str] = Field(default_factory=list, max_length=100)
    missing_evidence: list[str] = Field(default_factory=list, max_length=100)
    disclaimer: str = Field(min_length=1, max_length=1000)
