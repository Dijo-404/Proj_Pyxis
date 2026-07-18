"""Append-only audit event response contract."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend.app.schemas.common import Identifier


class AuditEventRead(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, populate_by_name=True)

    audit_id: Identifier
    case_id: Identifier | None
    actor_type: str
    actor_id: str
    action: str
    entity_type: str
    entity_id: str
    metadata: dict[str, Any] = Field(validation_alias="details", serialization_alias="metadata")
    created_at: datetime
