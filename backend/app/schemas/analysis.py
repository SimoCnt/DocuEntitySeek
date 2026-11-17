from uuid import UUID
from enum import Enum
from datetime import datetime
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


class AnalysisPipelineSummaryResponse(ApiModel):
    page_count: int
    document_characters: int

    entity_count: int
    visible_entity_count: int
    hidden_entity_count: int
    rejected_entity_count: int

    field_count: int
    field_candidate_count: int
    extracted_field_count: int
    ambiguous_field_count: int
    not_found_field_count: int
    rejected_field_candidate_count: int

    elapsed_ms: float


class AnalysisStartResponse(ApiModel):
    analysis_id: UUID
    status: str
    pipeline: AnalysisPipelineSummaryResponse


class AnalysisSummaryResponse(ApiModel):
    id: UUID
    document_id: UUID
    status: str
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None
    schema_version_id: UUID
    ai_runtime_config_id: UUID


class DocumentPageResponse(ApiModel):
    page_number: int
    text: str
    global_start: int
    global_end: int


class EntityOccurrenceResponse(ApiModel):
    id: UUID
    label: str
    text: str
    confidence: float
    global_start: int
    global_end: int
    page: int
    page_start: int
    page_end: int
    is_visible: bool


class FieldCandidateResponse(ApiModel):
    id: UUID
    value: str
    confidence: float
    page: int | None
    global_start: int
    global_end: int
    rank: int


class ExtractedFieldResponse(ApiModel):
    id: UUID
    field_key: str
    status: str
    value: str | None
    confidence: float | None
    page: int | None
    global_start: int | None
    global_end: int | None
    candidates: list[FieldCandidateResponse]


class AnalysisResultResponse(ApiModel):
    pages: list[DocumentPageResponse]
    entities: list[EntityOccurrenceResponse]
    fields: list[ExtractedFieldResponse]


class AnalysisDetailResponse(ApiModel):
    id: UUID
    document_id: UUID
    status: str
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None
    schema_version_id: UUID
    ai_runtime_config_id: UUID
    result: AnalysisResultResponse | None