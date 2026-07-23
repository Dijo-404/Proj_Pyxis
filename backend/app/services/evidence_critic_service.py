"""Application service for the audited Evidence Critic role (spec §13)."""

from sqlalchemy.orm import Session

from backend.app.schemas.assistant import CaseAnswer
from backend.app.services.audit_service import AuditService
from backend.app.services.case_service import CaseService
from local_ai.gemma.evidence_critic import EvidenceCritic


class EvidenceCriticService:
    def __init__(self, session: Session, critic: EvidenceCritic) -> None:
        self.session = session
        self.cases = CaseService(session)
        self.audit = AuditService(session)
        self.critic = critic

    async def critique(self, case_id: str, reviewer_id: str) -> CaseAnswer:
        risk_case = self.cases.get_case(case_id)
        answer = await self.critic.critique(risk_case)
        self.audit.record(
            action="EVIDENCE_CRITIQUED",
            entity_type="RISK_CASE",
            entity_id=case_id,
            actor_type="REVIEWER",
            actor_id=reviewer_id,
            case_id=case_id,
            metadata={"evidence_references": answer.evidence_references},
        )
        self.session.commit()
        return answer
