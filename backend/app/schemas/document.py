from enum import Enum
from datetime import date
from pydantic import Field
from app.schemas.base import ApiModel
from app.schemas.analysis import DocumentAnalysis



class DocumentStatus(str, Enum):
    READY = "READY"
    PROCESSING = "PROCESSING"
    ERROR = "ERROR"


class DocumentCategory(str, Enum):
    DISCIPLINARE = "DISCIPLINARE"
    CAPITOLATO = "CAPITOLATO"
    CONTRATTO = "CONTRATTO"
    BANDO = "BANDO"
    ALTRO = "ALTRO"


class DocumentSummary(ApiModel):
    id: str
    name: str = Field(min_length=1, max_length=255)
    category: DocumentCategory
    pages: int = Field(ge=0)
    status: DocumentStatus
    uploaded_at: date


class DocumentDetailResponse(ApiModel):
    document: DocumentSummary
    analysis: DocumentAnalysis | None = None