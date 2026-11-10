from typing import Annotated
from fastapi import Depends

from app.services.document_service import DocumentService


_document_service = DocumentService()


def get_document_service() -> DocumentService:
    return _document_service


DocumentServiceDep = Annotated[DocumentService, Depends(get_document_service)]