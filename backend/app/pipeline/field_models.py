"""Describe structured field candidates and aggregate model extraction outcomes."""

from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StructuredFieldCandidate:
    """Single structured field candidate with model score and provenance."""

    field_key: str
    value: str
    start: int
    end: int
    confidence: float
    record_index: int
    item_index: int

    @property
    def length(self) -> int:
        """Return the number of source-text characters in the candidate span."""

        return self.end - self.start


@dataclass(frozen=True, slots=True)
class StructuredExtractionResult:
    """Normalized field-extraction response, including missing fields."""

    candidates: tuple[StructuredFieldCandidate, ...]
    expected_field_keys: tuple[str, ...]
    record_count: int

    @property
    def total_candidates(self) -> int:
        """Return the total number of structured field candidates."""

        return len(self.candidates)

    @property
    def counts_by_field(self) -> dict[str, int]:
        """Return candidate counts grouped by schema field key."""

        return dict(Counter(candidate.field_key for candidate in self.candidates))

    @property
    def returned_field_keys(self) -> set[str]:
        """Return the field keys present in the model's extraction response."""

        return {candidate.field_key for candidate in self.candidates}

    @property
    def missing_field_keys(self) -> tuple[str, ...]:
        """Return requested fields with no model-proposed candidates."""

        returned = self.returned_field_keys
        return tuple(field_key for field_key in self.expected_field_keys if field_key not in returned)
