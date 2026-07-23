"""FastAPI dependencies shared by versioned routes."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.core.config import Settings, get_settings
from backend.app.core.database import get_db
from backend.app.services.errors import LocalAIUnavailableError
from local_ai.gemma.case_assistant import CaseAssistant
from local_ai.gemma.client import LocalGemmaClient
from local_ai.gemma.evidence_critic import EvidenceCritic
from local_ai.gemma.report_writer import ReportWriter

SettingsDependency = Annotated[Settings, Depends(get_settings)]
SessionDependency = Annotated[Session, Depends(get_db)]


def get_local_gemma_client(settings: SettingsDependency) -> LocalGemmaClient:
    try:
        return LocalGemmaClient(
            base_url=settings.gemma_base_url,
            model=settings.gemma_model,
            timeout_seconds=settings.gemma_timeout_seconds,
        )
    except ValueError as error:
        raise LocalAIUnavailableError(str(error)) from error


LocalGemmaDependency = Annotated[LocalGemmaClient, Depends(get_local_gemma_client)]


def get_case_assistant(client: LocalGemmaDependency) -> CaseAssistant:
    return CaseAssistant(client)


def get_report_writer(client: LocalGemmaDependency) -> ReportWriter:
    return ReportWriter(client)


def get_evidence_critic(client: LocalGemmaDependency) -> EvidenceCritic:
    return EvidenceCritic(CaseAssistant(client))


CaseAssistantDependency = Annotated[CaseAssistant, Depends(get_case_assistant)]
ReportWriterDependency = Annotated[ReportWriter, Depends(get_report_writer)]
EvidenceCriticDependency = Annotated[EvidenceCritic, Depends(get_evidence_critic)]
