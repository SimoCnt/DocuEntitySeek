import re
from uuid import uuid4
from pathlib import Path
from datetime import date

from app.core.exceptions import DocumentNotFoundError
from app.data.mock_documents import INITIAL_DOCUMENTS
from app.schemas.document import DocumentCategory, DocumentDetailResponse, DocumentStatus, DocumentSummary


class DocumentService:
    def __init__(self) -> None:
        self._documents = {item.document.id: item for item in INITIAL_DOCUMENTS}


    def list_documents(self) -> list[DocumentSummary]:
        return [item.document for item in self._documents.values()]


    def get_document(self, document_id: str) -> DocumentDetailResponse:
        document = self._documents.get(document_id)
        if document is None: raise DocumentNotFoundError(document_id)

        return document


    def create_document(self, *, file_name: str, category: DocumentCategory) -> DocumentSummary:
        document_id = self._build_document_id(file_name)
        summary = DocumentSummary(
            id=document_id,
            name=file_name,
            category=category,
            pages=0,
            status=DocumentStatus.PROCESSING,
            uploaded_at=date.today()            
        )
        self._documents[document_id] = DocumentDetailResponse(document=summary, analysis=None)        

        return summary


    @staticmethod
    def _build_document_id(file_name: str) -> str:
        stem = Path(file_name).stem.lower()
        slug = re.sub(r"[^a-z0-9]+", "-", stem).strip("-")

        if not slug: slug = "document"

        suffix = uuid4().hex[:8]

        return f"{slug}-{suffix}"