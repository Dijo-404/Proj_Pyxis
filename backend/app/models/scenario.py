"""Imported risk-scenario persistence model."""

from sqlalchemy import CheckConstraint, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models import Base


class Scenario(Base):
    __tablename__ = "scenarios"
    __table_args__ = (
        CheckConstraint("match_score >= 0 AND match_score <= 100", name="ck_scenario_match_score"),
    )

    scenario_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    case_id: Mapped[str] = mapped_column(
        ForeignKey("risk_cases.case_id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(16), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    match_score: Mapped[float] = mapped_column(Float)

    risk_case: Mapped["RiskCase"] = relationship(back_populates="scenarios")  # noqa: F821
