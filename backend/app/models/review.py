"""Human compliance-review decision persistence model."""

from datetime import UTC, datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.sql_types import UTCDateTime
from backend.app.models import Base


class Review(Base):
    __tablename__ = "reviews"

    review_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    case_id: Mapped[str] = mapped_column(
        ForeignKey("risk_cases.case_id", ondelete="CASCADE"), index=True
    )
    reviewer_id: Mapped[str] = mapped_column(String(128))
    action: Mapped[str] = mapped_column(String(32), index=True)
    reason: Mapped[str] = mapped_column(Text)
    previous_status: Mapped[str] = mapped_column(String(32))
    resulting_status: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=lambda: datetime.now(UTC))

    risk_case: Mapped["RiskCase"] = relationship(back_populates="reviews")  # noqa: F821
