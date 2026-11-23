from time import perf_counter
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.exceptions import DocumentNotFoundError, DocumentStorageError
from app.core.logging import get_logger
from app.pipeline.models import PreparedDocumentText
from app.pipeline.pdf_text_extractor import PdfTextExtractor
from app.pipeline.provenance import DocumentProvenanceBuilder
from app.repositories.document_page_repository import DocumentPageRepository
from app.repositories.document_repository import DocumentRepository
from app.services.document_storage import DocumentStorage


logger = get_logger("pipeline.preparation")


class DocumentPreparationService:
    def __init__(
        self,
        *,
        session: Session,
        storage: DocumentStorage,
        pdf_extractor: PdfTextExtractor,
        provenance_builder: DocumentProvenanceBuilder,
    ) -> None:
        self.session = session
        self.storage = storage
        self.pdf_extractor = pdf_extractor
        self.provenance_builder = provenance_builder
        self.documents = DocumentRepository(session)
        self.pages = DocumentPageRepository(session)


    def prepare(
            self, 
            *, 
            document_id: UUID, 
            owner_user_id: UUID
            ) -> PreparedDocumentText:
        started_at = perf_counter()

        logger.info(
            "TEXT_PREPARATION | phase=start | document_id=%s | owner_user_id=%s",
            document_id,
            owner_user_id,
        )

        try:
            document = self.documents.get_by_id_and_owner(document_id, owner_user_id)

            if document is None:
                raise DocumentNotFoundError(str(document_id))

            if not document.storage_key:
                logger.error("TEXT_PREPARATION | phase=storage_key_missing | document_id=%s", document_id)

                raise DocumentStorageError("Il documento non possiede un file persistito.")

            with self.storage.materialize(document.storage_key) as pdf_path:
                logger.info("TEXT_PREPARATION | phase=storage_resolved | document_id=%s", document_id)
                extraction = self.pdf_extractor.extract(document_id=document_id, pdf_path=pdf_path)
            prepared = self.provenance_builder.build(document_id=document_id, extraction=extraction)

            logger.info(
                "TEXT_PREPARATION | phase=persistence_start | document_id=%s | pages=%d",
                document_id,
                prepared.page_count,
            )

            self.pages.replace_for_document(document_id=document_id, pages=prepared.pages)
            document.page_count = prepared.page_count
            self.session.flush()

            elapsed_ms = (perf_counter() - started_at) * 1000

            logger.info(
                "TEXT_PREPARATION | phase=complete | document_id=%s | pages=%d | chars=%d | layout=%s | elapsed_ms=%.2f",
                document_id,
                prepared.page_count,
                prepared.total_characters,
                prepared.layout_version,
                elapsed_ms,
            )

            return prepared

        except Exception:
            logger.exception("TEXT_PREPARATION | phase=failed | document_id=%s", document_id)
            raise