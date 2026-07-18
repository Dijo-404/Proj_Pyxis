"""Risk-case import, retrieval, filtering, prioritization, and status use cases."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.case import RiskCase
from backend.app.repositories.case_repository import CaseRepository
from backend.app.schemas.case import RiskCaseImport, RiskCaseUpdate
from backend.app.schemas.common import CaseStatus, RiskLevel
from backend.app.services.audit_service import AuditService
from backend.app.services.errors import ConflictError, NotFoundError

PRIORITY_BY_RISK = {
    RiskLevel.CRITICAL: 1,
    RiskLevel.HIGH: 2,
    RiskLevel.MEDIUM: 3,
    RiskLevel.LOW: 4,
}

ADMINISTRATIVE_STATUSES = {
    CaseStatus.OPEN,
    CaseStatus.UNDER_REVIEW,
    CaseStatus.AWAITING_EVIDENCE,
    CaseStatus.ESCALATED,
}


class CaseService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = CaseRepository(session)
        self.audit = AuditService(session)

    def import_case(self, payload: RiskCaseImport) -> RiskCase:
        if self.repository.get(payload.case_id) is not None:
            raise ConflictError(
                code="CASE_ALREADY_EXISTS",
                message=f"case '{payload.case_id}' has already been imported",
            )

        try:
            risk_case = self.repository.add_import(
                payload, priority=PRIORITY_BY_RISK[payload.risk_level]
            )
            self.audit.record(
                action="CASE_IMPORTED",
                entity_type="RISK_CASE",
                entity_id=risk_case.case_id,
                actor_type="SYSTEM",
                actor_id="MEMBER_1_RISK_ENGINE",
                case_id=risk_case.case_id,
                metadata={
                    "risk_score": risk_case.risk_score,
                    "risk_level": risk_case.risk_level,
                    "scenario_count": len(payload.scenarios),
                },
            )
            self.session.commit()
        except IntegrityError as error:
            self.session.rollback()
            raise ConflictError(
                code="CASE_IMPORT_CONFLICT",
                message="case import contains an identifier that already exists",
            ) from error
        return risk_case

    def get_case(self, case_id: str) -> RiskCase:
        risk_case = self.repository.get(case_id)
        if risk_case is None:
            raise NotFoundError("case", case_id)
        return risk_case

    def list_cases(
        self,
        *,
        status: CaseStatus | None,
        risk_level: RiskLevel | None,
        customer_id: str | None,
        minimum_risk_score: float | None,
        offset: int,
        limit: int,
    ) -> list[RiskCase]:
        return self.repository.list(
            status=status.value if status else None,
            risk_level=risk_level.value if risk_level else None,
            customer_id=customer_id,
            minimum_risk_score=minimum_risk_score,
            offset=offset,
            limit=limit,
        )

    def update_case(self, case_id: str, payload: RiskCaseUpdate) -> RiskCase:
        risk_case = self.get_case(case_id)
        changes: dict[str, object] = {"reason": payload.reason}

        if payload.status is not None:
            if risk_case.status == CaseStatus.CLOSED.value:
                raise ConflictError(
                    code="CASE_ALREADY_CLOSED",
                    message="a closed case cannot be reopened through the case update API",
                )
            if payload.status not in ADMINISTRATIVE_STATUSES:
                raise ConflictError(
                    code="REVIEW_ACTION_REQUIRED",
                    message="cleared, suspicious, and closed dispositions require the review API",
                )
            changes["previous_status"] = risk_case.status
            changes["new_status"] = payload.status.value
            risk_case.status = payload.status.value

        if payload.priority is not None:
            changes["previous_priority"] = risk_case.priority
            changes["new_priority"] = payload.priority
            risk_case.priority = payload.priority

        self.audit.record(
            action="CASE_UPDATED",
            entity_type="RISK_CASE",
            entity_id=case_id,
            actor_type="REVIEWER",
            actor_id=payload.actor_id,
            case_id=case_id,
            metadata=changes,
        )
        self.session.commit()
        return risk_case
