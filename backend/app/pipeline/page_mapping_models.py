from dataclasses import dataclass
from enum import Enum

from app.pipeline.field_models import StructuredFieldCandidate
from app.pipeline.ner_models import NerCandidate


class SpanMappingFailureReason(str, Enum):
    START_IN_PAGE_SEPARATOR = "START_IN_PAGE_SEPARATOR"
    END_IN_PAGE_SEPARATOR = "END_IN_PAGE_SEPARATOR"
    CROSS_PAGE = "CROSS_PAGE"


@dataclass(frozen=True, slots=True)
class PageSpanCoordinates:
    page_number: int
    page_start: int
    page_end: int


@dataclass(frozen=True, slots=True)
class MappedNerOccurrence:
    candidate: NerCandidate
    page_number: int
    page_start: int
    page_end: int
    is_visible: bool


@dataclass(frozen=True, slots=True)
class RejectedNerCandidate:
    candidate: NerCandidate
    is_visible: bool
    reason: SpanMappingFailureReason


@dataclass(frozen=True, slots=True)
class NerPageMappingResult:
    mapped: tuple[MappedNerOccurrence, ...]
    rejected: tuple[RejectedNerCandidate, ...]

    @property
    def mapped_count(self) -> int:
        return len(self.mapped)

    @property
    def rejected_count(self) -> int:
        return len(self.rejected)


@dataclass(frozen=True, slots=True)
class MappedFieldCandidate:
    candidate: StructuredFieldCandidate
    page_number: int
    page_start: int
    page_end: int


@dataclass(frozen=True, slots=True)
class RejectedFieldCandidate:
    candidate: StructuredFieldCandidate
    reason: SpanMappingFailureReason


@dataclass(frozen=True, slots=True)
class FieldPageMappingResult:
    mapped: tuple[MappedFieldCandidate, ...]
    rejected: tuple[RejectedFieldCandidate, ...]

    @property
    def mapped_count(self) -> int:
        return len(self.mapped)

    @property
    def rejected_count(self) -> int:
        return len(self.rejected)