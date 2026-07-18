"""Secure local document upload, parsing, indexing, and verification use cases."""

import asyncio
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.models.document import Document
from backend.app.models.evidence import Evidence
from backend.app.repositories.document_repository import DocumentRepository
from backend.app.schemas.common import DocumentStatus, EvidenceStatus, EvidenceType
from backend.app.schemas.document import DocumentVerification
from backend.app.services.audit_service import AuditService
from backend.app.services.case_service import CaseService
from backend.app.services.errors import ConflictError, NotFoundError, ProcessingError
from document_processing.extractor import extract_structured_fields
from document_processing.indexer import build_index_entries
from document_processing.parser import SUPPORTED_EXTENSIONS, parse_document

READ_CHUNK_SIZE = 1024 * 1024


class DocumentService:
    def __init__(
        self,
        session: Session,
        *,
        storage_path: Path,
        max_document_bytes: int,
    ) -> None:
        self.session = session
        self.repository = DocumentRepository(session)
        self.cases = CaseService(session)
        self.audit = AuditService(session)
        self.storage_path = storage_path
        self.max_document_bytes = max_document_bytes

    async def upload(
        self,
        *,
        case_id: str,
        customer_id: str,
        document_type: str,
        uploaded_by: str,
        upload: UploadFile,
    ) -> Document:
        risk_case = self.cases.get_case(case_id)
        if risk_case.customer_id != customer_id:
            raise ConflictError(
                code="CUSTOMER_CASE_MISMATCH",
                message="document customer_id does not match the case customer",
            )

        original_filename = Path(upload.filename or "").name
        extension = Path(original_filename).suffix.lower()
        if not original_filename or extension not in SUPPORTED_EXTENSIONS:
            supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
            raise ProcessingError(
                code="UNSUPPORTED_DOCUMENT_TYPE",
                message=f"supported document extensions are: {supported}",
            )
        if not document_type.strip() or len(document_type) > 64:
            raise ProcessingError(
                code="INVALID_DOCUMENT_TYPE",
                message="document_type must contain between 1 and 64 characters",
            )

        document_id = f"DOC-{uuid4().hex}"
        case_directory = self.storage_path / case_id
        case_directory.mkdir(parents=True, exist_ok=True)
        destination = case_directory / f"{document_id}{extension}"
        digest = sha256()
        size = 0

        try:
            with destination.open("xb") as output:
                while chunk := await upload.read(READ_CHUNK_SIZE):
                    size += len(chunk)
                    if size > self.max_document_bytes:
                        raise ProcessingError(
                            code="DOCUMENT_TOO_LARGE",
                            message=f"document exceeds {self.max_document_bytes} bytes",
                        )
                    digest.update(chunk)
                    output.write(chunk)

            parsed = await asyncio.to_thread(parse_document, destination)
            extracted_data = await asyncio.to_thread(
                extract_structured_fields, parsed.text, parsed.metadata
            )
            index_entries = await asyncio.to_thread(
                build_index_entries, document_id=document_id, text=parsed.text
            )
        except ProcessingError:
            destination.unlink(missing_ok=True)
            raise
        except (OSError, RuntimeError, ValueError) as error:
            destination.unlink(missing_ok=True)
            raise ProcessingError(code="DOCUMENT_PROCESSING_FAILED", message=str(error)) from error

        document = self.repository.add(
            Document(
                document_id=document_id,
                case_id=case_id,
                customer_id=customer_id,
                document_type=document_type.strip().upper(),
                original_filename=original_filename,
                content_type=upload.content_type or "application/octet-stream",
                file_path=str(destination.resolve()),
                sha256=digest.hexdigest(),
                size_bytes=size,
                extracted_data=extracted_data,
                index_entries=index_entries,
                verification_status=DocumentStatus.UNVERIFIED.value,
                uploaded_by=uploaded_by,
            )
        )
        evidence = Evidence(
            evidence_id=f"EVD-{uuid4().hex}",
            case_id=case_id,
            evidence_type=EvidenceType.DOCUMENT.value,
            description=f"Reviewer uploaded {document.document_type}: {original_filename}",
            source_reference=document_id,
            status=EvidenceStatus.UNVERIFIED.value,
            confidence=0.5,
            submitted_by=uploaded_by,
        )
        self.session.add(evidence)
        self.audit.record(
            action="DOCUMENT_UPLOADED",
            entity_type="DOCUMENT",
            entity_id=document_id,
            actor_type="REVIEWER",
            actor_id=uploaded_by,
            case_id=case_id,
            metadata={
                "filename": original_filename,
                "document_type": document.document_type,
                "sha256": document.sha256,
                "size_bytes": size,
            },
        )
        try:
            self.session.commit()
        except SQLAlchemyError as error:
            self.session.rollback()
            destination.unlink(missing_ok=True)
            raise ProcessingError(
                code="DOCUMENT_PERSISTENCE_FAILED",
                message="document metadata could not be stored",
            ) from error
        return document

    def list_for_case(self, case_id: str) -> list[Document]:
        self.cases.get_case(case_id)
        return self.repository.list_for_case(case_id)

    def verify(self, document_id: str, payload: DocumentVerification) -> Document:
        document = self.repository.get(document_id)
        if document is None:
            raise NotFoundError("document", document_id)
        if payload.status is DocumentStatus.UNVERIFIED:
            raise ConflictError(
                code="INVALID_DOCUMENT_VERIFICATION",
                message="document verification must result in VERIFIED or REJECTED",
            )

        previous_status = document.verification_status
        document.verification_status = payload.status.value
        document.verified_by = payload.reviewer_id
        document.verified_at = datetime.now(UTC)

        evidence_statement = select(Evidence).where(
            Evidence.case_id == document.case_id,
            Evidence.source_reference == document_id,
        )
        for evidence in self.session.scalars(evidence_statement):
            evidence.status = (
                EvidenceStatus.VERIFIED.value
                if payload.status is DocumentStatus.VERIFIED
                else EvidenceStatus.CONTRADICTED.value
            )
            evidence.verified_by = payload.reviewer_id
            evidence.verification_reason = payload.reason
            evidence.verified_at = document.verified_at

        self.audit.record(
            action="DOCUMENT_VERIFIED",
            entity_type="DOCUMENT",
            entity_id=document_id,
            actor_type="REVIEWER",
            actor_id=payload.reviewer_id,
            case_id=document.case_id,
            metadata={
                "previous_status": previous_status,
                "new_status": document.verification_status,
                "reason": payload.reason,
            },
        )
        self.session.commit()
        return document
