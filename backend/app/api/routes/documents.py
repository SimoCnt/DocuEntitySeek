from typing import Annotated
from fastapi import APIRouter, File, Form, Path, UploadFile, status

from app.schemas.common import ErrorResponse
from app.dependencies import DocumentServiceDep
from app.services.file_validation import validate_pdf_upload
from app.schemas.document import DocumentCategory, DocumentDetailResponse, DocumentSummary


router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    responses={
        422: {
            "model": ErrorResponse,
            "description": "Request validation failed."
        }
    }
)


@router.get(
    "",
    response_model=list[DocumentSummary],
    summary="List documents",
)
async def list_documents(service: DocumentServiceDep) -> list[DocumentSummary]:
    return service.list_documents()


@router.get(
    "/{document_id}",
    response_model=DocumentDetailResponse,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Document not found.",
        }
    },
    summary="Get document detail",
)
async def get_document(document_id: Annotated[str, Path(min_length=1, max_length=120)], service: DocumentServiceDep) -> DocumentDetailResponse:
    return service.get_document(document_id)


@router.post(
    "",
    response_model=DocumentSummary,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid PDF file."
        }
    },
    summary="Create document",
)
async def create_document(
    file: Annotated[UploadFile, File(description="PDF document to upload.")],
    category: Annotated[DocumentCategory, Form()],
    service: DocumentServiceDep,
) -> DocumentSummary:
    await validate_pdf_upload(file)

    return service.create_document(file_name=(file.filename or "document.pdf"), category=category)