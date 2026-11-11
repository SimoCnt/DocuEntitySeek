
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.exceptions import DocumentNotFoundError
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentCategory, DocumentDetailResponse, DocumentSummary
from app.services.document_mapper import build_document_analysis, to_document_summary


class DocumentService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.documents = DocumentRepository(session)
        self.analyses = AnalysisRepository(session)


    def list_documents(self, owner_user_id: UUID) -> list[DocumentSummary]:
        documents = self.documents.list_by_owner(owner_user_id)

        return [to_document_summary(document) for document in documents]


    def get_document(self, document_id: UUID, owner_user_id: UUID) -> DocumentDetailResponse:
        document = self.documents.get_by_id_and_owner(document_id, owner_user_id)

        if document is None:
            raise DocumentNotFoundError(str(document_id))

        analysis = self.analyses.get_latest_completed(document.id)
        api_analysis = build_document_analysis(document, analysis) if analysis is not None else None

        return DocumentDetailResponse(document=to_document_summary(document), analysis=api_analysis)


    def create_document(
        self,
        *,
        owner_user_id: UUID,
        file_name: str,
        category: DocumentCategory,
        mime_type: str | None,
        size_bytes: int | None,
    ) -> DocumentSummary:
        document = self.documents.create(
            owner_user_id=owner_user_id,
            original_name=file_name,
            category=category.value,
            mime_type=mime_type,
            size_bytes=size_bytes,
        )
        self.session.commit()
        self.session.refresh(document)
        return to_document_summary(document)
