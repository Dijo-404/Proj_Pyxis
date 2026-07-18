"""Compliance risk-case persistence model."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, CheckConstraint, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.sql_types import UTCDateTime
from backend.app.models import Base


class RiskCase(Base):
    """Member 2's persisted representation of an imported risk case."""

    __tablename__ = "risk_cases"
    __table_args__ = (
        CheckConstraint("risk_score >= 0 AND risk_score <= 100", name="ck_case_risk_score"),
        CheckConstraint("priority >= 1 AND priority <= 5", name="ck_case_priority"),
    )

    case_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    customer_id: Mapped[str] = mapped_column(String(128), index=True)
    risk_score: Mapped[float] = mapped_column(Float)
    risk_level: Mapped[str] = mapped_column(String(16), index=True)
    status: Mapped[str] = mapped_column(String(32), default="OPEN", index=True)
    priority: Mapped[int] = mapped_column(Integer, default=3, index=True)
    anomalies: Mapped[list[str]] = mapped_column(JSON, default=list)
    decision_critical_evidence: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    recommended_actions: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime(),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    scenarios: Mapped[list["Scenario"]] = relationship(  # noqa: F821
        back_populates="risk_case", cascade="all, delete-orphan", lazy="selectin"
    )
    evidence: Mapped[list["Evidence"]] = relationship(  # noqa: F821
        back_populates="risk_case", cascade="all, delete-orphan", lazy="selectin"
    )
    documents: Mapped[list["Document"]] = relationship(  # noqa: F821
        back_populates="risk_case", cascade="all, delete-orphan", lazy="selectin"
    )
    reviews: Mapped[list["Review"]] = relationship(  # noqa: F821
        back_populates="risk_case", cascade="all, delete-orphan", lazy="selectin"
    )
    reports: Mapped[list["ComplianceReport"]] = relationship(  # noqa: F821
        back_populates="risk_case", cascade="all, delete-orphan", lazy="selectin"
    )
