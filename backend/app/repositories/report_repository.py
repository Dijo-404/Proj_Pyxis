"""Generated compliance-report persistence operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.compliance_report import ComplianceReport


class ReportRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, report_id: str) -> ComplianceReport | None:
        return self.session.get(ComplianceReport, report_id)

    def latest_for_case(self, case_id: str) -> ComplianceReport | None:
        statement = (
            select(ComplianceReport)
            .where(ComplianceReport.case_id == case_id)
            .order_by(ComplianceReport.created_at.desc())
            .limit(1)
        )
        return self.session.scalar(statement)

    def add(self, report: ComplianceReport) -> ComplianceReport:
        self.session.add(report)
        self.session.flush()
        return report
