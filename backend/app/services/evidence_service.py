"""Reviewer evidence management and verification use cases."""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from backend.app.models.evidence import Evidence
from backend.app.models.scenario import Scenario
from backend.app.repositories.evidence_repository import EvidenceRepository
from backend.app.schemas.common import EvidenceStatus
from backend.app.schemas.evidence import EvidenceCreate, EvidenceVerification
from backend.app.services.audit_service import AuditService
from backend.app.services.case_service import CaseService
from backend.app.services.errors import ConflictError, NotFoundError


class EvidenceService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = EvidenceRepository(session)
        self.cases = CaseService(session)
        self.audit = AuditService(session)

    def list_for_case(self, case_id: str) -> list[Evidence]:
        self.cases.get_case(case_id)
        return self.repository.list_for_case(case_id)

    def add(self, case_id: str, payload: EvidenceCreate) -> Evidence:
        self.cases.get_case(case_id)
        if payload.scenario_id is not None:
            scenario = self.session.get(Scenario, payload.scenario_id)
            if scenario is None or scenario.case_id != case_id:
                raise ConflictError(
                    code="SCENARIO_CASE_MISMATCH",
                    message="scenario does not belong to the requested case",
                )

        evidence = self.repository.add(
            Evidence(
                evidence_id=f"EVD-{uuid4().hex}",
                case_id=case_id,
                scenario_id=payload.scenario_id,
                evidence_type=payload.evidence_type.value,
                description=payload.description,
                source_reference=payload.source_reference,
                status=EvidenceStatus.UNVERIFIED.value,
                confidence=payload.confidence,
                submitted_by=payload.submitted_by,
            )
        )
        self.audit.record(
            action="EVIDENCE_ADDED",
            entity_type="EVIDENCE",
            entity_id=evidence.evidence_id,
            actor_type="REVIEWER",
            actor_id=payload.submitted_by,
            case_id=case_id,
            metadata={"evidence_type": evidence.evidence_type},
        )
        self.session.commit()
        return evidence

    def verify(self, evidence_id: str, payload: EvidenceVerification) -> Evidence:
        evidence = self.repository.get(evidence_id)
        if evidence is None:
            raise NotFoundError("evidence", evidence_id)
        if payload.status not in {EvidenceStatus.VERIFIED, EvidenceStatus.CONTRADICTED}:
            raise ConflictError(
                code="INVALID_VERIFICATION_STATUS",
                message="verification status must be VERIFIED or CONTRADICTED",
            )

        previous_status = evidence.status
        evidence.status = payload.status.value
        evidence.verified_by = payload.reviewer_id
        evidence.verification_reason = payload.reason
        evidence.verified_at = datetime.now(UTC)
        self.audit.record(
            action="EVIDENCE_VERIFIED",
            entity_type="EVIDENCE",
            entity_id=evidence_id,
            actor_type="REVIEWER",
            actor_id=payload.reviewer_id,
            case_id=evidence.case_id,
            metadata={
                "previous_status": previous_status,
                "new_status": evidence.status,
                "reason": payload.reason,
            },
        )
        self.session.commit()
        return evidence
