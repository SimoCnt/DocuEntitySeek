from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NerCandidate:
    label: str
    text: str
    start: int
    end: int
    confidence: float


    @property
    def length(self) -> int:
        return self.end - self.start


@dataclass(frozen=True, slots=True)
class NerExtractionResult:
    candidates: tuple[NerCandidate, ...]


    @property
    def total_candidates(self) -> int:
        return len(self.candidates)


    @property
    def counts_by_label(self) -> dict[str, int]:
        return dict(Counter(candidate.label for candidate in self.candidates))