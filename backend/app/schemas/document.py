"""Define the public document metadata and lifecycle contracts."""

from uuid import UUID
from enum import Enum
from datetime import date
from pydantic import Field
from app.schemas.base import ApiModel


class DocumentStatus(str, Enum):
    """Constrain accepted values for document status."""

    UPLOADED = "UPLOADED"
    READY = "READY"
    PROCESSING = "PROCESSING"
    ERROR = "ERROR"



class DocumentSummary(ApiModel):
    """Define the typed API contract for document summary."""

    id: UUID
    name: str = Field(min_length=1, max_length=255)
    pages: int = Field(ge=0)
    status: DocumentStatus
    uploaded_at: date


class DocumentDetailResponse(ApiModel):
    """Serialize the document detail data returned by the REST API."""

    document: DocumentSummary
