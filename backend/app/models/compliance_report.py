"""Generated compliance-report persistence model."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.sql_types import UTCDateTime
from backend.app.models import Base


class ComplianceReport(Base):
    __tablename__ = "compliance_reports"

    report_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    case_id: Mapped[str] = mapped_column(
        ForeignKey("risk_cases.case_id", ondelete="CASCADE"), index=True
    )
    status: Mapped[str] = mapped_column(String(32), index=True)
    narrative: Mapped[str] = mapped_column(Text)
    structured_report: Mapped[dict[str, Any]] = mapped_column(JSON)
    html_path: Mapped[str] = mapped_column(String(1024))
    pdf_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    generated_by: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=lambda: datetime.now(UTC))

    risk_case: Mapped["RiskCase"] = relationship(back_populates="reports")  # noqa: F821
