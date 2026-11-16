from dataclasses import dataclass
from enum import Enum

from app.pipeline.field_models import StructuredFieldCandidate
from app.pipeline.page_mapping_models import SpanMappingFailureReason


class FieldStatus(str, Enum):
    EXTRACTED = "EXTRACTED"
    AMBIGUOUS = "AMBIGUOUS"
    NOT_FOUND = "NOT_FOUND"
    ERROR = "ERROR"


@dataclass(frozen=True, slots=True)
class RankedFieldCandidate:
    candidate: StructuredFieldCandidate
    rank: int
    page_number: int | None
    mapping_failure_reason: SpanMappingFailureReason | None = None

    @property
    def is_page_mapped(self) -> bool:
        return self.page_number is not None


@dataclass(frozen=True, slots=True)
class ResolvedExtractedField:
    field_key: str
    status: FieldStatus
    value: str | None
    confidence: float | None
    page_number: int | None
    global_start: int | None
    global_end: int | None
    candidates: tuple[RankedFieldCandidate, ...]


@dataclass(frozen=True, slots=True)
class FieldResolutionResult:
    fields: tuple[ResolvedExtractedField, ...]

    @property
    def total_fields(self) -> int:
        return len(self.fields)

    @property
    def total_candidates(self) -> int:
        return sum(len(field.candidates) for field in self.fields)

    @property
    def extracted_count(self) -> int:
        return sum(field.status == FieldStatus.EXTRACTED for field in self.fields)

    @property
    def ambiguous_count(self) -> int:
        return sum(field.status == FieldStatus.AMBIGUOUS for field in self.fields)

    @property
    def not_found_count(self) -> int:
        return sum(field.status == FieldStatus.NOT_FOUND for field in self.fields)