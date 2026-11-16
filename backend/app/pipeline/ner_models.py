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


@dataclass(frozen=True, slots=True)
class ViewerNerDecision:
    candidate: NerCandidate
    is_visible: bool
    blocked_by: NerCandidate | None = None


@dataclass(frozen=True, slots=True)
class ViewerNerSelectionResult:
    decisions: tuple[ViewerNerDecision, ...]


    @property
    def visible_candidates(self) -> tuple[NerCandidate, ...]:
        return tuple(decision.candidate for decision in self.decisions if decision.is_visible)


    @property
    def hidden_candidates(self) -> tuple[NerCandidate, ...]:
        return tuple(decision.candidate for decision in self.decisions if not decision.is_visible)


    @property
    def visible_count(self) -> int:
        return len(self.visible_candidates)


    @property
    def hidden_count(self) -> int:
        return len(self.hidden_candidates)