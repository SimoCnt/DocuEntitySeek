
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import DocumentModel


class DocumentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session


    def list_by_owner(self, owner_user_id: UUID) -> list[DocumentModel]:
        statement = (
            select(DocumentModel)
            .where(DocumentModel.owner_user_id == owner_user_id)
            .order_by(DocumentModel.created_at.desc())
        )
        
        return list(self.session.scalars(statement).all())


    def get_by_id_and_owner(self, document_id: UUID, owner_user_id: UUID) -> DocumentModel | None:
        statement = (
            select(DocumentModel)
            .where(DocumentModel.id == document_id, DocumentModel.owner_user_id == owner_user_id)
            .options(selectinload(DocumentModel.pages))
        )

        return self.session.scalar(statement)
    

    def create(
        self,
        *,
        owner_user_id: UUID,
        original_name: str,
        category: str,
        mime_type: str | None,
        size_bytes: int | None,
    ) -> DocumentModel:
        document = DocumentModel(
            owner_user_id=owner_user_id,
            original_name=original_name,
            category=category,
            status="PROCESSING",
            mime_type=mime_type,
            size_bytes=size_bytes,
            page_count=None,
            storage_key=None,
        )
        self.session.add(document)
        self.session.flush()

        return document
