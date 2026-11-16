from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StructuredFieldCandidate:
    field_key: str
    value: str
    start: int
    end: int
    confidence: float
    record_index: int
    item_index: int

    @property
    def length(self) -> int:
        return self.end - self.start


@dataclass(frozen=True, slots=True)
class StructuredExtractionResult:
    candidates: tuple[StructuredFieldCandidate, ...]
    expected_field_keys: tuple[str, ...]
    record_count: int

    @property
    def total_candidates(self) -> int:
        return len(self.candidates)

    @property
    def counts_by_field(self) -> dict[str, int]:
        return dict(Counter(candidate.field_key for candidate in self.candidates))

    @property
    def returned_field_keys(self) -> set[str]:
        return {candidate.field_key for candidate in self.candidates}

    @property
    def missing_field_keys(self) -> tuple[str, ...]:
        returned = self.returned_field_keys
        return tuple(field_key for field_key in self.expected_field_keys if field_key not in returned)