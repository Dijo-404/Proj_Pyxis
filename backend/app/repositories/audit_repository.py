"""Append-only audit-log persistence operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.audit_log import AuditLog


class AuditRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, event: AuditLog) -> AuditLog:
        self.session.add(event)
        self.session.flush()
        return event

    def list_for_case(self, case_id: str) -> list[AuditLog]:
        statement = (
            select(AuditLog).where(AuditLog.case_id == case_id).order_by(AuditLog.created_at.asc())
        )
        return list(self.session.scalars(statement).all())
