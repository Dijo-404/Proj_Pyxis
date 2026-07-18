"""AI-produced and reviewer-uploaded evidence persistence model."""

from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.sql_types import UTCDateTime
from backend.app.models import Base


class Evidence(Base):
    __tablename__ = "evidence"
    __table_args__ = (
        CheckConstraint("confidence >= 0 AND confidence <= 1", name="ck_evidence_confidence"),
    )

    evidence_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    case_id: Mapped[str] = mapped_column(
        ForeignKey("risk_cases.case_id", ondelete="CASCADE"), index=True
    )
    scenario_id: Mapped[str | None] = mapped_column(
        ForeignKey("scenarios.scenario_id", ondelete="SET NULL"), nullable=True
    )
    evidence_type: Mapped[str] = mapped_column(String(32), index=True)
    description: Mapped[str] = mapped_column(Text)
    source_reference: Mapped[str] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(32), index=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    submitted_by: Mapped[str] = mapped_column(String(128))
    verification_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    verified_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=lambda: datetime.now(UTC))

    risk_case: Mapped["RiskCase"] = relationship(back_populates="evidence")  # noqa: F821
