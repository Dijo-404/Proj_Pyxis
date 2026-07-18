"""Document upload, verification, and response contracts."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from backend.app.schemas.common import DocumentStatus, Identifier, LongText


class DocumentVerification(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal[DocumentStatus.VERIFIED, DocumentStatus.REJECTED]
    reviewer_id: Identifier
    reason: LongText


class DocumentRead(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    document_id: Identifier
    case_id: Identifier
    customer_id: Identifier
    document_type: str
    original_filename: str
    content_type: str
    sha256: str
    size_bytes: int
    extracted_data: dict[str, Any]
    verification_status: DocumentStatus
    uploaded_by: str
    verified_by: str | None
    created_at: datetime
    verified_at: datetime | None
