"""Evidence persistence operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.evidence import Evidence


class EvidenceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, evidence_id: str) -> Evidence | None:
        return self.session.get(Evidence, evidence_id)

    def list_for_case(self, case_id: str) -> list[Evidence]:
        statement = (
            select(Evidence).where(Evidence.case_id == case_id).order_by(Evidence.created_at.asc())
        )
        return list(self.session.scalars(statement).all())

    def add(self, evidence: Evidence) -> Evidence:
        self.session.add(evidence)
        self.session.flush()
        return evidence
