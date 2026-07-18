"""Local document upload, listing, and verification endpoints."""

from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile, status

from backend.app.api.dependencies import SessionDependency, SettingsDependency
from backend.app.schemas.common import Identifier
from backend.app.schemas.document import DocumentRead, DocumentVerification
from backend.app.services.document_service import DocumentService

router = APIRouter(tags=["documents"])


@router.post(
    "/documents/upload",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    session: SessionDependency,
    settings: SettingsDependency,
    case_id: Annotated[Identifier, Form()],
    customer_id: Annotated[Identifier, Form()],
    document_type: Annotated[str, Form(min_length=1, max_length=64)],
    uploaded_by: Annotated[Identifier, Form()],
    file: Annotated[UploadFile, File()],
) -> DocumentRead:
    service = DocumentService(
        session,
        storage_path=settings.document_storage_path,
        max_document_bytes=settings.max_document_bytes,
    )
    document = await service.upload(
        case_id=case_id,
        customer_id=customer_id,
        document_type=document_type,
        uploaded_by=uploaded_by,
        upload=file,
    )
    return DocumentRead.model_validate(document)


@router.get("/cases/{case_id}/documents", response_model=list[DocumentRead])
def list_documents(
    case_id: Identifier,
    session: SessionDependency,
    settings: SettingsDependency,
) -> list[DocumentRead]:
    service = DocumentService(
        session,
        storage_path=settings.document_storage_path,
        max_document_bytes=settings.max_document_bytes,
    )
    return [DocumentRead.model_validate(item) for item in service.list_for_case(case_id)]


@router.post("/documents/{document_id}/verify", response_model=DocumentRead)
def verify_document(
    document_id: Identifier,
    payload: DocumentVerification,
    session: SessionDependency,
    settings: SettingsDependency,
) -> DocumentRead:
    service = DocumentService(
        session,
        storage_path=settings.document_storage_path,
        max_document_bytes=settings.max_document_bytes,
    )
    return DocumentRead.model_validate(service.verify(document_id, payload))
