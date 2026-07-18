"""Compliance report contracts."""

from pydantic import BaseModel, ConfigDict


class ReportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    requested_by: str


class ReportReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    report_id: str
    case_id: str
    local_path: str
