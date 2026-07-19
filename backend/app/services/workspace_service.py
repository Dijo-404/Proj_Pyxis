"""Read-model assembly for web and mobile clients."""

from collections import Counter
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from backend.app.core.config import Settings
from backend.app.models.case import RiskCase
from backend.app.repositories.report_repository import ReportRepository
from backend.app.schemas.case import RiskCaseRead
from backend.app.schemas.report import ReportRead
from backend.app.schemas.workspace import (
    DashboardStats,
    ModelRuntime,
    ReviewerProfile,
    TrendPoint,
    WorkspaceBootstrap,
)
from backend.app.services.case_service import CaseService

OPEN_STATUSES = {"OPEN", "UNDER_REVIEW", "AWAITING_EVIDENCE", "ESCALATED"}


class WorkspaceService:
    def __init__(self, session: Session, settings: Settings) -> None:
        self.session = session
        self.settings = settings

    def bootstrap(self) -> WorkspaceBootstrap:
        cases = CaseService(self.session).list_cases(
            status=None,
            risk_level=None,
            customer_id=None,
            minimum_risk_score=None,
            offset=0,
            limit=200,
        )
        reports = ReportRepository(self.session).list_recent(limit=50)
        return WorkspaceBootstrap(
            reviewer=ReviewerProfile(
                reviewer_id=self.settings.reviewer_id,
                name=self.settings.reviewer_name,
                email=self.settings.reviewer_email,
                role=self.settings.reviewer_role,
            ),
            dashboard=self._dashboard(cases),
            cases=[RiskCaseRead.model_validate(case) for case in cases],
            reports=[ReportRead.model_validate(report) for report in reports],
            model_runtime=ModelRuntime(
                provider=self.settings.gemma_provider,
                model=self.settings.gemma_model,
                base_url=self.settings.gemma_base_url,
            ),
        )

    def _dashboard(self, cases: list[RiskCase]) -> DashboardStats:
        now = datetime.now(UTC)
        dates = [(now - timedelta(days=offset)).date() for offset in range(6, -1, -1)]
        flagged_counts = Counter(case.created_at.date() for case in cases)
        open_cases = [case for case in cases if case.status in OPEN_STATUSES]
        cleared = [case for case in cases if case.status == "CLEARED"]
        suspicious = [case for case in cases if case.status == "SUSPICIOUS"]
        resolved_count = len(cleared) + len(suspicious)
        false_positive_rate = (
            round((len(cleared) / resolved_count) * 100, 1) if resolved_count else 0.0
        )
        transactions_analyzed = sum(
            int(case.workspace_data.get("transaction_count", 0))
            for case in cases
        )
        return DashboardStats(
            transactions_analyzed=transactions_analyzed,
            open_cases=len(open_cases),
            critical_cases=sum(case.risk_score >= 80 for case in open_cases),
            pending_reviews=sum(
                case.status in {"UNDER_REVIEW", "AWAITING_EVIDENCE"}
                for case in cases
            ),
            cleared_today=sum(
                case.status == "CLEARED" and case.updated_at.date() == now.date()
                for case in cases
            ),
            false_positive_rate=false_positive_rate,
            flagged_trend=[
                TrendPoint(date=day, label=day.strftime("%a"), value=flagged_counts[day])
                for day in dates
            ],
        )
