"""Define typed results and rejection reasons for mapping text spans back to PDF pages."""

from dataclasses import dataclass
from enum import Enum

from app.pipeline.field_models import StructuredFieldCandidate
from app.pipeline.ner_models import NerCandidate


class SpanMappingFailureReason(str, Enum):
    """Reason an extracted text span cannot be mapped to a PDF page."""

    START_IN_PAGE_SEPARATOR = "START_IN_PAGE_SEPARATOR"
    END_IN_PAGE_SEPARATOR = "END_IN_PAGE_SEPARATOR"
    CROSS_PAGE = "CROSS_PAGE"


@dataclass(frozen=True, slots=True)
class PageSpanCoordinates:
    """Page-local coordinates resolved from a global text span."""

    page_number: int
    page_start: int
    page_end: int


@dataclass(frozen=True, slots=True)
class MappedNerOccurrence:
    """Entity candidate successfully associated with its PDF page."""

    candidate: NerCandidate
    page_number: int
    page_start: int
    page_end: int
    is_visible: bool


@dataclass(frozen=True, slots=True)
class RejectedNerCandidate:
    """Entity candidate rejected when provenance or mapping checks fail."""

    candidate: NerCandidate
    is_visible: bool
    reason: SpanMappingFailureReason


@dataclass(frozen=True, slots=True)
class NerPageMappingResult:
    """Successful and rejected entity-to-page mappings."""

    mapped: tuple[MappedNerOccurrence, ...]
    rejected: tuple[RejectedNerCandidate, ...]

    @property
    def mapped_count(self) -> int:
        """Count entity occurrences with valid page coordinates."""

        return len(self.mapped)

    @property
    def rejected_count(self) -> int:
        """Count rejected entity-to-page mappings."""

        return len(self.rejected)


@dataclass(frozen=True, slots=True)
class MappedFieldCandidate:
    """Structured field candidate mapped to a page and local offsets."""

    candidate: StructuredFieldCandidate
    page_number: int
    page_start: int
    page_end: int


@dataclass(frozen=True, slots=True)
class RejectedFieldCandidate:
    """Field candidate rejected during text provenance mapping."""

    candidate: StructuredFieldCandidate
    reason: SpanMappingFailureReason


@dataclass(frozen=True, slots=True)
class FieldPageMappingResult:
    """Successful and rejected field-candidate page mappings."""

    mapped: tuple[MappedFieldCandidate, ...]
    rejected: tuple[RejectedFieldCandidate, ...]

    @property
    def mapped_count(self) -> int:
        """Count field candidates with valid page coordinates."""

        return len(self.mapped)

    @property
    def rejected_count(self) -> int:
        """Count rejected structured field candidate spans."""

        return len(self.rejected)
