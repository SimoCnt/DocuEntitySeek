"""Define Pydantic contracts for analysis execution, history, extraction results, and PDF geometry.
"""

from uuid import UUID
from enum import Enum
from datetime import datetime
from pydantic import Field
from typing import Annotated, Literal
from app.schemas.base import ApiModel


class EntityDefinition(ApiModel):
    """Define the typed API contract for entity definition."""

    label: str
    color: str


class TextOnlySegment(ApiModel):
    """Define the typed API contract for text only segment."""

    type: Literal["text"]
    text: str


class EntitySegment(ApiModel):
    """Define the typed API contract for entity segment."""

    type: Literal["entity"]
    id: UUID
    text: str
    label: str


TextSegment = Annotated[TextOnlySegment | EntitySegment, Field(discriminator="type")]


class DocumentPage(ApiModel):
    """Define the typed API contract for document page."""

    page_number: int = Field(ge=1)
    segments: list[TextSegment]


class ExtractedFieldStatus(str, Enum):
    """Constrain accepted values for extracted field status."""

    EXTRACTED = "EXTRACTED"
    AMBIGUOUS = "AMBIGUOUS"
    NOT_FOUND = "NOT_FOUND"
    ERROR = "ERROR"


class ExtractedField(ApiModel):
    """Define the typed API contract for extracted field."""

    id: UUID
    label: str
    value: str | None = None
    page: int | None = Field(default=None, ge=1)
    confidence: float | None = Field(default=None, ge=0, le=1)
    status: ExtractedFieldStatus


class DocumentAnalysis(ApiModel):
    """Define the typed API contract for document analysis."""

    entity_definitions: list[EntityDefinition]
    pages: list[DocumentPage]
    extracted_fields: list[ExtractedField]


class AnalysisPipelineSummaryResponse(ApiModel):
    """Serialize the analysis pipeline summary data returned by the REST API."""

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
    """Serialize the analysis start data returned by the REST API."""

    analysis_id: UUID
    status: str
    pipeline: AnalysisPipelineSummaryResponse


class AnalysisSummaryResponse(ApiModel):
    """Serialize the analysis summary data returned by the REST API."""

    id: UUID
    document_id: UUID
    status: str
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None
    schema_version_id: UUID
    schema_name: str
    schema_version: int
    ai_runtime_config_id: UUID


class DocumentPageResponse(ApiModel):
    """Serialize the document page data returned by the REST API."""

    page_number: int
    text: str
    global_start: int
    global_end: int


class EntityOccurrenceResponse(ApiModel):
    """Serialize the entity occurrence data returned by the REST API."""

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
    """Serialize the field candidate data returned by the REST API."""

    id: UUID
    value: str
    confidence: float
    page: int | None
    global_start: int
    global_end: int
    rank: int


class ExtractedFieldResponse(ApiModel):
    """Serialize the extracted field data returned by the REST API."""

    id: UUID
    field_key: str
    status: str
    value: str | None
    confidence: float | None
    page: int | None
    global_start: int | None
    global_end: int | None
    candidates: list[FieldCandidateResponse]


class AnalysisEntityDefinitionResponse(ApiModel):
    """Serialize the analysis entity definition data returned by the REST API."""

    label: str
    description: str
    color: str
    sort_order: int


class AnalysisFieldDefinitionResponse(ApiModel):
    """Serialize the analysis field definition data returned by the REST API."""

    field_key: str
    label: str
    description: str
    data_type: str
    is_required: bool
    sort_order: int


class AnalysisSchemaResponse(ApiModel):
    """Serialize the analysis schema data returned by the REST API."""

    schema_id: UUID
    schema_version_id: UUID
    name: str
    domain: str
    version: int
    entity_definitions: list[AnalysisEntityDefinitionResponse]
    field_definitions: list[AnalysisFieldDefinitionResponse]


class AnalysisResultResponse(ApiModel):
    """Serialize the analysis result data returned by the REST API."""

    schema: AnalysisSchemaResponse
    pages: list[DocumentPageResponse]
    entities: list[EntityOccurrenceResponse]
    fields: list[ExtractedFieldResponse]


class AnalysisDetailResponse(ApiModel):
    """Serialize the analysis detail data returned by the REST API."""

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


class AnalysisStartRequest(ApiModel):
    """Validate the analysis start request payload exposed by the REST API."""

    schema_version_id: UUID | None = None


class PdfHighlightRect(ApiModel):
    """Define the typed API contract for pdf highlight rect."""

    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)
    width: float = Field(gt=0, le=1)
    height: float = Field(gt=0, le=1)


class PdfHighlightRegion(ApiModel):
    """Define the typed API contract for pdf highlight region."""

    kind: Literal["entity", "field"]
    id: UUID
    label: str
    rects: list[PdfHighlightRect]


class PdfPageGeometryResponse(ApiModel):
    """Serialize the pdf page geometry data returned by the REST API."""

    page_number: int = Field(ge=1)
    aligned: bool
    regions: list[PdfHighlightRegion]
