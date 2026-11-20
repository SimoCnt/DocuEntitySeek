from uuid import UUID
from enum import Enum
from datetime import date
from pydantic import Field
from app.schemas.base import ApiModel


class DocumentStatus(str, Enum):
    UPLOADED = "UPLOADED"
    READY = "READY"
    PROCESSING = "PROCESSING"
    ERROR = "ERROR"



class DocumentSummary(ApiModel):
    id: UUID
    name: str = Field(min_length=1, max_length=255)
    pages: int = Field(ge=0)
    status: DocumentStatus
    uploaded_at: date


class DocumentDetailResponse(ApiModel):
    document: DocumentSummary
