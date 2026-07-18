"""Local compliance-document metadata persistence model."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.sql_types import UTCDateTime
from backend.app.models import Base


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (CheckConstraint("size_bytes >= 0", name="ck_document_size"),)

    document_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    case_id: Mapped[str] = mapped_column(
        ForeignKey("risk_cases.case_id", ondelete="CASCADE"), index=True
    )
    customer_id: Mapped[str] = mapped_column(String(128), index=True)
    document_type: Mapped[str] = mapped_column(String(64))
    original_filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(128))
    file_path: Mapped[str] = mapped_column(String(1024), unique=True)
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    size_bytes: Mapped[int] = mapped_column(Integer)
    extracted_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    index_entries: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    verification_status: Mapped[str] = mapped_column(String(32), default="UNVERIFIED")
    uploaded_by: Mapped[str] = mapped_column(String(128))
    verified_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=lambda: datetime.now(UTC))
    verified_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)

    risk_case: Mapped["RiskCase"] = relationship(back_populates="documents")  # noqa: F821
