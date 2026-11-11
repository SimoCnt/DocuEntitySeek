from uuid import UUID
from enum import Enum
from pydantic import Field
from typing import Annotated, Literal
from app.schemas.base import ApiModel


class EntityDefinition(ApiModel):
    label: str
    color: str


class TextOnlySegment(ApiModel):
    type: Literal["text"]
    text: str


class EntitySegment(ApiModel):
    type: Literal["entity"]
    id: UUID
    text: str
    label: str


TextSegment = Annotated[TextOnlySegment | EntitySegment, Field(discriminator="type")]


class DocumentPage(ApiModel):
    page_number: int = Field(ge=1)
    segments: list[TextSegment]


class ExtractedFieldStatus(str, Enum):
    EXTRACTED = "EXTRACTED"
    AMBIGUOUS = "AMBIGUOUS"
    NOT_FOUND = "NOT_FOUND"
    ERROR = "ERROR"


class ExtractedField(ApiModel):
    id: UUID
    label: str
    value: str | None = None
    page: int | None = Field(default=None, ge=1)
    confidence: float | None = Field(default=None, ge=0, le=1)
    status: ExtractedFieldStatus


class DocumentAnalysis(ApiModel):
    entity_definitions: list[EntityDefinition]
    pages: list[DocumentPage]
    extracted_fields: list[ExtractedField]