"""Shared API response models and strict compliance-domain types."""

from enum import StrEnum
from typing import Annotated, Generic, TypeVar

from pydantic import BaseModel, StringConstraints

T = TypeVar("T")

Identifier = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=128,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$",
    ),
]
ShortText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
LongText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=10_000)]


class ApiResponse(BaseModel, Generic[T]):
    data: T


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


class RiskLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CaseStatus(StrEnum):
    OPEN = "OPEN"
    UNDER_REVIEW = "UNDER_REVIEW"
    AWAITING_EVIDENCE = "AWAITING_EVIDENCE"
    ESCALATED = "ESCALATED"
    CLEARED = "CLEARED"
    SUSPICIOUS = "SUSPICIOUS"
    CLOSED = "CLOSED"


class ScenarioCategory(StrEnum):
    LEGITIMATE = "LEGITIMATE"
    SUSPICIOUS = "SUSPICIOUS"
    UNCERTAIN = "UNCERTAIN"


class EvidenceStatus(StrEnum):
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    CONTRADICTED = "CONTRADICTED"
    MISSING = "MISSING"


class EvidenceType(StrEnum):
    SUPPORTING = "SUPPORTING"
    CONTRADICTING = "CONTRADICTING"
    MISSING = "MISSING"
    REVIEWER = "REVIEWER"
    DOCUMENT = "DOCUMENT"


class ReviewAction(StrEnum):
    CLEAR = "CLEAR"
    REQUEST_MORE_EVIDENCE = "REQUEST_MORE_EVIDENCE"
    ESCALATE = "ESCALATE"
    MARK_SUSPICIOUS = "MARK_SUSPICIOUS"
    CLOSE = "CLOSE"


class DocumentStatus(StrEnum):
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    REJECTED = "REJECTED"


class ReportStatus(StrEnum):
    GENERATED = "GENERATED"
