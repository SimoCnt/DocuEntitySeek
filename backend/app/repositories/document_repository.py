"""Store document metadata and enforce owner-scoped document queries."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import DocumentModel


class DocumentRepository:
    """Persist document metadata and enforce owner-scoped queries."""

    def __init__(self, session: Session) -> None:
        self.session = session


    def list_by_owner(self, owner_user_id: UUID) -> list[DocumentModel]:
        """List documents belonging to the specified user."""

        statement = (
            select(DocumentModel)
            .where(DocumentModel.owner_user_id == owner_user_id)
            .options(selectinload(DocumentModel.analyses))
            .order_by(DocumentModel.created_at.desc())
        )

        return list(self.session.scalars(statement).all())


    def get_by_id_and_owner(self, document_id: UUID, owner_user_id: UUID) -> DocumentModel | None:
        """Fetch a document only when its owner matches the caller."""

        statement = (
            select(DocumentModel)
            .where(
                DocumentModel.id == document_id,
                DocumentModel.owner_user_id == owner_user_id,
            )
            .options(
                selectinload(DocumentModel.pages),
                selectinload(DocumentModel.analyses),
            )
        )

        return self.session.scalar(statement)


    def create(
        self,
        *,
        owner_user_id: UUID,
        original_name: str,
        mime_type: str | None,
        size_bytes: int | None,
    ) -> DocumentModel:
        """Create an uploaded-document metadata row within the caller's transaction."""

        document = DocumentModel(
            owner_user_id=owner_user_id,
            original_name=original_name,
            status="UPLOADED",
            mime_type=mime_type,
            size_bytes=size_bytes,
            page_count=None,
            storage_key=None,
        )

        self.session.add(document)
        self.session.flush()

        return document
