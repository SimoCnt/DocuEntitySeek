"""Expose owner-scoped PDF upload, metadata, listing, and authenticated byte-range download
endpoints.
"""

from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Header, File, Path, UploadFile, status

from app.dependencies import DocumentServiceDep, CurrentUserDep
from app.schemas.common import ErrorResponse
from app.schemas.document import DocumentDetailResponse, DocumentSummary
from app.services.file_validation import validate_pdf_upload
from app.services.pdf_content_response import build_pdf_response


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
    """List the current user's uploaded documents."""

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
    """Return metadata for an owned document."""

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
    service: DocumentServiceDep,
    current_user: CurrentUserDep,
) -> DocumentSummary:
    """Validate and persist a PDF upload for the current user."""

    validate_pdf_upload(file)

    return service.create_document(
        owner_user_id=current_user.id,
        file_name=file.filename or "document.pdf",
        mime_type=file.content_type,
        size_bytes=file.size,
        file_stream=file.file
    )


@router.get("/{document_id}/file", summary="Read original PDF (authenticated, supports byte ranges)")
def read_original_pdf(
    document_id: Annotated[UUID, Path()],
    service: DocumentServiceDep,
    current_user: CurrentUserDep,
    byte_range: Annotated[str | None, Header(alias="Range")] = None,
):
    """Stream an owned original PDF with optional HTTP Range support."""

    storage_key = service.get_original_storage_key(document_id, current_user.id)
    return build_pdf_response(service.storage, storage_key, byte_range)
