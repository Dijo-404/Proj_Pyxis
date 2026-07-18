"""Evidence matrix contracts."""

from pydantic import BaseModel, ConfigDict, Field


class EvidenceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str
    description: str
    source_reference: str
    status: str
    confidence: float = Field(ge=0, le=1)
