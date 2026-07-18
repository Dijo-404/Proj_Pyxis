"""Application service for audited, case-scoped Gemma questions."""

from hashlib import sha256

from sqlalchemy.orm import Session

from backend.app.schemas.assistant import CaseAnswer, CaseQuestion
from backend.app.services.audit_service import AuditService
from backend.app.services.case_service import CaseService
from local_ai.gemma.case_assistant import CaseAssistant


class AssistantService:
    def __init__(self, session: Session, assistant: CaseAssistant) -> None:
        self.session = session
        self.cases = CaseService(session)
        self.audit = AuditService(session)
        self.assistant = assistant

    async def ask(self, case_id: str, payload: CaseQuestion) -> CaseAnswer:
        risk_case = self.cases.get_case(case_id)
        answer = await self.assistant.answer(risk_case=risk_case, question=payload.question)
        question_digest = sha256(payload.question.encode("utf-8")).hexdigest()
        self.audit.record(
            action="GEMMA_ASSISTANT_QUERIED",
            entity_type="RISK_CASE",
            entity_id=case_id,
            actor_type="REVIEWER",
            actor_id=payload.reviewer_id,
            case_id=case_id,
            metadata={
                "question_sha256": question_digest,
                "evidence_references": answer.evidence_references,
            },
        )
        self.session.commit()
        return answer
