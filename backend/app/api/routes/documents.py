
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, File, Form, Path, UploadFile, status

from app.dependencies import DocumentServiceDep, CurrentUserDep
from app.schemas.common import ErrorResponse
from app.schemas.document import DocumentCategory, DocumentDetailResponse, DocumentSummary
from app.services.file_validation import validate_pdf_upload


router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    responses={422: {"model": ErrorResponse, "description": "Request validation failed."}},
)


@router.get(
    "", 
    response_model=list[DocumentSummary], 
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Insufficient permissions"}
    },
    summary="List documents"
    )
def list_documents(service: DocumentServiceDep, current_user: CurrentUserDep) -> list[DocumentSummary]:
    return service.list_documents(current_user.id)


@router.get(
    "/{document_id}",
    response_model=DocumentDetailResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Document not found."},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Insufficient permissions"}
        },
    summary="Get document detail"
)
def get_document(
    document_id: Annotated[UUID, Path()],
    service: DocumentServiceDep,
    current_user: CurrentUserDep
) -> DocumentDetailResponse:
    return service.get_document(document_id, current_user.id)


@router.post(
    "",
    response_model=DocumentSummary,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid PDF file."},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Insufficient permissions"}
        },
    summary="Create document",
)
def create_document(
    file: Annotated[UploadFile, File(description="PDF document to upload.")],
    category: Annotated[DocumentCategory, Form()],
    service: DocumentServiceDep,
    current_user: CurrentUserDep,
) -> DocumentSummary:
    validate_pdf_upload(file)

    return service.create_document(
        owner_user_id=current_user.id,
        file_name=file.filename or "document.pdf",
        category=category,
        mime_type=file.content_type,
        size_bytes=file.size,
    )
