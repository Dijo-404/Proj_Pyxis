"""Append-only audit trail service."""

from typing import Any
from uuid import uuid4

from sqlalchemy.orm import Session

from backend.app.models.audit_log import AuditLog
from backend.app.repositories.audit_repository import AuditRepository


class AuditService:
    def __init__(self, session: Session) -> None:
        self.repository = AuditRepository(session)

    def record(
        self,
        *,
        action: str,
        entity_type: str,
        entity_id: str,
        actor_type: str,
        actor_id: str,
        case_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditLog:
        """Append an event within the caller's current transaction."""
        return self.repository.add(
            AuditLog(
                audit_id=f"AUD-{uuid4().hex}",
                case_id=case_id,
                actor_type=actor_type,
                actor_id=actor_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                details=metadata or {},
            )
        )

    def list_for_case(self, case_id: str) -> list[AuditLog]:
        return self.repository.list_for_case(case_id)
