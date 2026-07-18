"""Validated local Gemma report generation and deterministic export use cases."""

import asyncio
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.models.case import RiskCase
from backend.app.models.compliance_report import ComplianceReport
from backend.app.repositories.report_repository import ReportRepository
from backend.app.schemas.common import ReportStatus
from backend.app.schemas.report import ReportNarrative, ReportRequest
from backend.app.services.audit_service import AuditService
from backend.app.services.case_service import CaseService
from backend.app.services.errors import NotFoundError, ProcessingError
from local_ai.gemma.context_builder import build_case_context
from report_engine.export import export_html, export_pdf
from report_engine.renderer import render_investigation_report


class NarrativeWriter(Protocol):
    async def write(self, risk_case: RiskCase) -> ReportNarrative: ...


class ReportService:
    def __init__(
        self,
        session: Session,
        *,
        writer: NarrativeWriter | None,
        output_path: Path,
    ) -> None:
        self.session = session
        self.repository = ReportRepository(session)
        self.cases = CaseService(session)
        self.audit = AuditService(session)
        self.writer = writer
        self.output_path = output_path

    async def generate(self, case_id: str, payload: ReportRequest) -> ComplianceReport:
        risk_case = self.cases.get_case(case_id)
        if self.writer is None:
            raise RuntimeError("a narrative writer is required to generate a report")
        narrative = await self.writer.write(risk_case)
        generated_at = datetime.now(UTC)
        report_id = f"RPT-{uuid4().hex}"
        case_context = build_case_context(risk_case)
        narrative_data = narrative.model_dump(mode="json")
        structured_report = {
            **case_context,
            "narrative": narrative_data,
            "generated_at": generated_at.isoformat(),
            "generated_by": payload.generated_by,
        }
        template_context = {
            "case_id": case_id,
            "customer_id": risk_case.customer_id,
            "risk_score": risk_case.risk_score,
            "risk_level": risk_case.risk_level,
            "case_status": risk_case.status,
            "generated_at": generated_at.isoformat(),
            "generated_by": payload.generated_by,
            "narrative": narrative_data,
            "scenarios": case_context["scenarios"],
            "evidence": case_context["evidence"],
            "reviews": case_context["reviews"],
        }

        destination_directory = self.output_path / case_id
        html_path = destination_directory / f"{report_id}.html"
        pdf_path = destination_directory / f"{report_id}.pdf"
        try:
            html = await asyncio.to_thread(render_investigation_report, template_context)
            await asyncio.to_thread(export_html, html, html_path)
            exported_pdf = (
                await asyncio.to_thread(export_pdf, html, pdf_path) if payload.include_pdf else None
            )
        except (OSError, RuntimeError, ValueError) as error:
            html_path.unlink(missing_ok=True)
            pdf_path.unlink(missing_ok=True)
            raise ProcessingError(code="REPORT_EXPORT_FAILED", message=str(error)) from error

        narrative_text = "\n\n".join(
            (
                narrative.executive_summary,
                narrative.risk_assessment,
                narrative.evidence_analysis,
                narrative.reviewer_decision,
                narrative.limitations,
            )
        )
        report = self.repository.add(
            ComplianceReport(
                report_id=report_id,
                case_id=case_id,
                status=ReportStatus.GENERATED.value,
                narrative=narrative_text,
                structured_report=structured_report,
                html_path=str(html_path.resolve()),
                pdf_path=str(exported_pdf.resolve()) if exported_pdf else None,
                generated_by=payload.generated_by,
                created_at=generated_at,
            )
        )
        self.audit.record(
            action="REPORT_GENERATED",
            entity_type="COMPLIANCE_REPORT",
            entity_id=report_id,
            actor_type="REVIEWER",
            actor_id=payload.generated_by,
            case_id=case_id,
            metadata={"html_path": report.html_path, "pdf_generated": exported_pdf is not None},
        )
        try:
            self.session.commit()
        except SQLAlchemyError as error:
            self.session.rollback()
            html_path.unlink(missing_ok=True)
            pdf_path.unlink(missing_ok=True)
            raise ProcessingError(
                code="REPORT_PERSISTENCE_FAILED",
                message="generated report metadata could not be stored",
            ) from error
        return report

    def latest_for_case(self, case_id: str) -> ComplianceReport:
        self.cases.get_case(case_id)
        report = self.repository.latest_for_case(case_id)
        if report is None:
            raise NotFoundError("report for case", case_id)
        return report
