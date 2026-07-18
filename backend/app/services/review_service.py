"""Human reviewer decisions and controlled case-status transitions."""

from uuid import uuid4

from sqlalchemy.orm import Session

from backend.app.models.review import Review
from backend.app.repositories.review_repository import ReviewRepository
from backend.app.schemas.common import CaseStatus, ReviewAction
from backend.app.schemas.review import ReviewCreate
from backend.app.services.audit_service import AuditService
from backend.app.services.case_service import CaseService
from backend.app.services.errors import ConflictError

RESULTING_STATUS = {
    ReviewAction.CLEAR: CaseStatus.CLEARED,
    ReviewAction.REQUEST_MORE_EVIDENCE: CaseStatus.AWAITING_EVIDENCE,
    ReviewAction.ESCALATE: CaseStatus.ESCALATED,
    ReviewAction.MARK_SUSPICIOUS: CaseStatus.SUSPICIOUS,
    ReviewAction.CLOSE: CaseStatus.CLOSED,
}


class ReviewService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = ReviewRepository(session)
        self.cases = CaseService(session)
        self.audit = AuditService(session)

    def review(self, case_id: str, payload: ReviewCreate) -> Review:
        risk_case = self.cases.get_case(case_id)
        previous_status = CaseStatus(risk_case.status)

        if previous_status is CaseStatus.CLOSED:
            raise ConflictError(
                code="CASE_ALREADY_CLOSED",
                message="a closed case cannot receive another review action",
            )
        if payload.action is ReviewAction.CLOSE and previous_status not in {
            CaseStatus.CLEARED,
            CaseStatus.SUSPICIOUS,
        }:
            raise ConflictError(
                code="FINAL_DISPOSITION_REQUIRED",
                message="a case must be cleared or marked suspicious before it can be closed",
            )

        resulting_status = RESULTING_STATUS[payload.action]
        review = self.repository.add(
            Review(
                review_id=f"REV-{uuid4().hex}",
                case_id=case_id,
                reviewer_id=payload.reviewer_id,
                action=payload.action.value,
                reason=payload.reason,
                previous_status=previous_status.value,
                resulting_status=resulting_status.value,
            )
        )
        risk_case.status = resulting_status.value
        self.audit.record(
            action=f"CASE_{payload.action.value}",
            entity_type="RISK_CASE",
            entity_id=case_id,
            actor_type="REVIEWER",
            actor_id=payload.reviewer_id,
            case_id=case_id,
            metadata={
                "review_id": review.review_id,
                "previous_status": previous_status.value,
                "resulting_status": resulting_status.value,
                "reason": payload.reason,
            },
        )
        self.session.commit()
        return review

    def list_for_case(self, case_id: str) -> list[Review]:
        self.cases.get_case(case_id)
        return self.repository.list_for_case(case_id)
