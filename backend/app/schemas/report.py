"""Compliance report generation and response contracts."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from backend.app.schemas.common import Identifier, ReportStatus


class ReportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_by: Identifier
    include_pdf: bool = True


class ReportNarrative(BaseModel):
    model_config = ConfigDict(extra="forbid")

    executive_summary: str = Field(min_length=1, max_length=20_000)
    risk_assessment: str = Field(min_length=1, max_length=20_000)
    evidence_analysis: str = Field(min_length=1, max_length=20_000)
    reviewer_decision: str = Field(min_length=1, max_length=20_000)
    limitations: str = Field(min_length=1, max_length=10_000)


class ReportRead(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    report_id: Identifier
    case_id: Identifier
    status: ReportStatus
    narrative: str
    structured_report: dict[str, object]
    html_path: str
    pdf_path: str | None
    generated_by: Identifier
    created_at: datetime
