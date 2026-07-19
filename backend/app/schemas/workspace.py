"""Shared bootstrap contracts consumed by the web and mobile workspaces."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from backend.app.schemas.case import RiskCaseRead
from backend.app.schemas.report import ReportRead


class TrendPoint(BaseModel):
    date: date
    label: str
    value: int = Field(ge=0)


class DashboardStats(BaseModel):
    transactions_analyzed: int = Field(ge=0)
    open_cases: int = Field(ge=0)
    critical_cases: int = Field(ge=0)
    pending_reviews: int = Field(ge=0)
    cleared_today: int = Field(ge=0)
    false_positive_rate: float = Field(ge=0, le=100)
    flagged_trend: list[TrendPoint]


class ReviewerProfile(BaseModel):
    reviewer_id: str
    name: str
    email: str
    role: str


class ModelRuntime(BaseModel):
    provider: str
    model: str
    base_url: str
    local_only: bool = True


class WorkspaceBootstrap(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reviewer: ReviewerProfile
    dashboard: DashboardStats
    cases: list[RiskCaseRead]
    reports: list[ReportRead]
    model_runtime: ModelRuntime
