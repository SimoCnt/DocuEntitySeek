from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.models import DocumentPageModel
from app.pipeline.models import PreparedDocumentPage


class DocumentPageRepository:
    def __init__(self, session: Session) -> None:
        self.session = session


    def replace_for_document(
            self, 
            *, 
            document_id: UUID, 
            pages: tuple[PreparedDocumentPage, ...]
            ) -> list[DocumentPageModel]:
        self.session.execute(
            delete(DocumentPageModel).where(DocumentPageModel.document_id == document_id)
)

        models = [
            DocumentPageModel(
                document_id=document_id,
                page_number=page.page_number,
                extracted_text=page.text,
                global_start=page.global_start,
                global_end=page.global_end,
            )
            for page in pages
        ]

        self.session.add_all(models)
        self.session.flush()

        return models

    def list_for_document(self, document_id: UUID) -> list[DocumentPageModel]:
        statement = (
            select(DocumentPageModel)
            .where(DocumentPageModel.document_id == document_id)
            .order_by(DocumentPageModel.page_number)
        )

        return list(self.session.scalars(statement).all())