
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, File, Form, Path, UploadFile, status

from app.dependencies import DevelopmentUserIdDep, DocumentServiceDep
from app.schemas.common import ErrorResponse
from app.schemas.document import DocumentCategory, DocumentDetailResponse, DocumentSummary
from app.services.file_validation import validate_pdf_upload


router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    responses={422: {"model": ErrorResponse, "description": "Request validation failed."}},
)


@router.get("", response_model=list[DocumentSummary], summary="List documents")
def list_documents(service: DocumentServiceDep, owner_user_id: DevelopmentUserIdDep) -> list[DocumentSummary]:
    return service.list_documents(owner_user_id)


@router.get(
    "/{document_id}",
    response_model=DocumentDetailResponse,
    responses={404: {"model": ErrorResponse, "description": "Document not found."}},
    summary="Get document detail",
)
def get_document(
    document_id: Annotated[UUID, Path()],
    service: DocumentServiceDep,
    owner_user_id: DevelopmentUserIdDep,
) -> DocumentDetailResponse:
    return service.get_document(document_id, owner_user_id)


@router.post(
    "",
    response_model=DocumentSummary,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse, "description": "Invalid PDF file."}},
    summary="Create document",
)
def create_document(
    file: Annotated[UploadFile, File(description="PDF document to upload.")],
    category: Annotated[DocumentCategory, Form()],
    service: DocumentServiceDep,
    owner_user_id: DevelopmentUserIdDep,
) -> DocumentSummary:
    validate_pdf_upload(file)

    return service.create_document(
        owner_user_id=owner_user_id,
        file_name=file.filename or "document.pdf",
        category=category,
        mime_type=file.content_type,
        size_bytes=file.size,
    )
