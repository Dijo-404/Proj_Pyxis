"""Evidence, local Gemma, human review, and audit endpoints."""

from fastapi import APIRouter, status

from backend.app.api.dependencies import (
    CaseAssistantDependency,
    EvidenceCriticDependency,
    SessionDependency,
)
from backend.app.schemas.assistant import CaseAnswer, CaseCritiqueRequest, CaseQuestion
from backend.app.schemas.audit import AuditEventRead
from backend.app.schemas.common import Identifier
from backend.app.schemas.evidence import EvidenceCreate, EvidenceRead, EvidenceVerification
from backend.app.schemas.review import ReviewCreate, ReviewRead
from backend.app.services.assistant_service import AssistantService
from backend.app.services.audit_service import AuditService
from backend.app.services.case_service import CaseService
from backend.app.services.evidence_critic_service import EvidenceCriticService
from backend.app.services.evidence_service import EvidenceService
from backend.app.services.review_service import ReviewService

router = APIRouter(tags=["investigations"])


@router.get("/cases/{case_id}/evidence", response_model=list[EvidenceRead])
def list_evidence(case_id: Identifier, session: SessionDependency) -> list[EvidenceRead]:
    evidence = EvidenceService(session).list_for_case(case_id)
    return [EvidenceRead.model_validate(item) for item in evidence]


@router.post(
    "/cases/{case_id}/evidence",
    response_model=EvidenceRead,
    status_code=status.HTTP_201_CREATED,
)
def add_evidence(
    case_id: Identifier, payload: EvidenceCreate, session: SessionDependency
) -> EvidenceRead:
    return EvidenceRead.model_validate(EvidenceService(session).add(case_id, payload))


@router.patch("/evidence/{evidence_id}/verify", response_model=EvidenceRead)
def verify_evidence(
    evidence_id: Identifier,
    payload: EvidenceVerification,
    session: SessionDependency,
) -> EvidenceRead:
    return EvidenceRead.model_validate(EvidenceService(session).verify(evidence_id, payload))


@router.post(
    "/cases/{case_id}/review",
    response_model=ReviewRead,
    status_code=status.HTTP_201_CREATED,
)
def review_case(
    case_id: Identifier, payload: ReviewCreate, session: SessionDependency
) -> ReviewRead:
    return ReviewRead.model_validate(ReviewService(session).review(case_id, payload))


@router.get("/cases/{case_id}/reviews", response_model=list[ReviewRead])
def list_reviews(case_id: Identifier, session: SessionDependency) -> list[ReviewRead]:
    reviews = ReviewService(session).list_for_case(case_id)
    return [ReviewRead.model_validate(review) for review in reviews]


@router.get("/cases/{case_id}/audit", response_model=list[AuditEventRead])
def list_audit_events(case_id: Identifier, session: SessionDependency) -> list[AuditEventRead]:
    CaseService(session).get_case(case_id)
    events = AuditService(session).list_for_case(case_id)
    return [AuditEventRead.model_validate(event) for event in events]


@router.post("/cases/{case_id}/ask-gemma", response_model=CaseAnswer)
async def ask_gemma(
    case_id: Identifier,
    payload: CaseQuestion,
    session: SessionDependency,
    assistant: CaseAssistantDependency,
) -> CaseAnswer:
    return await AssistantService(session, assistant).ask(case_id, payload)


@router.post("/cases/{case_id}/critique-evidence", response_model=CaseAnswer)
async def critique_evidence(
    case_id: Identifier,
    payload: CaseCritiqueRequest,
    session: SessionDependency,
    critic: EvidenceCriticDependency,
) -> CaseAnswer:
    """Runs the Evidence Critic role: challenges the leading scenario and identifies
    contradictory, unverified, and missing evidence for a human reviewer.
    """
    return await EvidenceCriticService(session, critic).critique(case_id, payload.reviewer_id)
