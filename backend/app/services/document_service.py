
from uuid import UUID
from sqlalchemy.orm import Session
from time import perf_counter
from typing import BinaryIO

from app.core.logging import get_logger
from app.core.exceptions import DocumentNotFoundError
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentCategory, DocumentDetailResponse, DocumentSummary
from app.services.document_mapper import build_document_analysis, to_document_summary
from app.services.document_storage import DocumentStorage


logger = get_logger("document")


class DocumentService:
    def __init__(self, session: Session, storage: DocumentStorage) -> None:
        self.session = session
        self.storage = storage
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
        file_stream: BinaryIO,
    ) -> DocumentSummary:
        started_at = perf_counter()
        storage_key: str | None = None

        logger.info(
            "DOCUMENT_CREATE | phase=start | owner_user_id=%s | filename=%r | category=%s | size_bytes=%s",
            owner_user_id,
            file_name,
            category.value,
            size_bytes,
        )

        try:
            document = self.documents.create(
                owner_user_id=owner_user_id,
                original_name=file_name,
                category=category.value,
                mime_type=mime_type,
                size_bytes=size_bytes,
            )

            logger.info("DOCUMENT_CREATE | phase=db_record_created | document_id=%s", document.id)

            storage_key = self.storage.save_original(
                owner_user_id=owner_user_id,
                document_id=document.id,
                source=file_stream,
            )

            document.storage_key = storage_key

            logger.info(
                "DOCUMENT_CREATE | phase=storage_linked | document_id=%s | storage_key=%s",
                document.id,
                storage_key,
            )

            self.session.commit()
            self.session.refresh(document)

            elapsed_ms = (perf_counter() - started_at) * 1000

            logger.info(
                "DOCUMENT_CREATE | phase=complete | document_id=%s | elapsed_ms=%.2f",
                document.id,
                elapsed_ms,
            )

            return to_document_summary(document)

        except Exception:
            self.session.rollback()

            if storage_key:
                try:
                    self.storage.delete(storage_key)
                except Exception:
                    logger.exception("DOCUMENT_CREATE | phase=rollback_storage_cleanup_failed | storage_key=%s", storage_key)

            logger.exception(
                "DOCUMENT_CREATE | phase=failed | owner_user_id=%s | filename=%r",
                owner_user_id,
                file_name,
            )

            raise
