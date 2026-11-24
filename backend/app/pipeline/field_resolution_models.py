"""Represent ranked field candidates, extraction status, and resolved information-extraction
results.
"""

from dataclasses import dataclass
from enum import Enum

from app.pipeline.field_models import StructuredFieldCandidate
from app.pipeline.page_mapping_models import SpanMappingFailureReason


class FieldStatus(str, Enum):
    """Possible resolution outcomes for an extracted field."""

    EXTRACTED = "EXTRACTED"
    AMBIGUOUS = "AMBIGUOUS"
    NOT_FOUND = "NOT_FOUND"
    ERROR = "ERROR"


@dataclass(frozen=True, slots=True)
class RankedFieldCandidate:
    """Candidate field value enriched with page mapping and ranking metadata."""

    candidate: StructuredFieldCandidate
    rank: int
    page_number: int | None
    mapping_failure_reason: SpanMappingFailureReason | None = None

    @property
    def is_page_mapped(self) -> bool:
        """Report whether a field candidate has valid source-page coordinates."""

        return self.page_number is not None


@dataclass(frozen=True, slots=True)
class ResolvedExtractedField:
    """Final field value or unresolved status selected from ranked candidates."""

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
    """Aggregate resolved fields and extraction-quality counters."""

    fields: tuple[ResolvedExtractedField, ...]

    @property
    def total_fields(self) -> int:
        """Return the number of schema fields processed during resolution."""

        return len(self.fields)

    @property
    def total_candidates(self) -> int:
        """Return the number of ranked candidates across resolved fields."""

        return sum(len(field.candidates) for field in self.fields)

    @property
    def extracted_count(self) -> int:
        """Count fields resolved to an extracted value."""

        return sum(field.status == FieldStatus.EXTRACTED for field in self.fields)

    @property
    def ambiguous_count(self) -> int:
        """Count fields with ambiguous candidate values."""

        return sum(field.status == FieldStatus.AMBIGUOUS for field in self.fields)

    @property
    def not_found_count(self) -> int:
        """Count schema fields without an accepted value."""

        return sum(field.status == FieldStatus.NOT_FOUND for field in self.fields)
