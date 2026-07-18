"""Local document metadata persistence operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.document import Document


class DocumentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, document_id: str) -> Document | None:
        return self.session.get(Document, document_id)

    def list_for_case(self, case_id: str) -> list[Document]:
        statement = (
            select(Document).where(Document.case_id == case_id).order_by(Document.created_at.asc())
        )
        return list(self.session.scalars(statement).all())

    def add(self, document: Document) -> Document:
        self.session.add(document)
        self.session.flush()
        return document
