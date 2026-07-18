"""Append-only compliance audit event persistence model."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.sql_types import UTCDateTime
from backend.app.models import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    audit_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    case_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    actor_type: Mapped[str] = mapped_column(String(32))
    actor_id: Mapped[str] = mapped_column(String(128))
    action: Mapped[str] = mapped_column(String(64), index=True)
    entity_type: Mapped[str] = mapped_column(String(64))
    entity_id: Mapped[str] = mapped_column(String(128), index=True)
    details: Mapped[dict[str, Any]] = mapped_column("metadata_json", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=lambda: datetime.now(UTC), index=True
    )
