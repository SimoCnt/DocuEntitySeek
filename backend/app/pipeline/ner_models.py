"""Represent NER candidates and the decisions used to display overlapping entities."""

from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NerCandidate:
    """Single candidate entity with a label, span, text, and confidence."""

    label: str
    text: str
    start: int
    end: int
    confidence: float


    @property
    def length(self) -> int:
        """Return the source-text length of this entity span."""

        return self.end - self.start


@dataclass(frozen=True, slots=True)
class NerExtractionResult:
    """Normalized collection of NER candidates and per-label counts."""

    candidates: tuple[NerCandidate, ...]


    @property
    def total_candidates(self) -> int:
        """Return the number of normalized entity candidates."""

        return len(self.candidates)


    @property
    def counts_by_label(self) -> dict[str, int]:
        """Return candidate counts grouped by entity label."""

        return dict(Counter(candidate.label for candidate in self.candidates))


@dataclass(frozen=True, slots=True)
class ViewerNerDecision:
    """Display or hiding decision for a candidate entity span."""

    candidate: NerCandidate
    is_visible: bool
    blocked_by: NerCandidate | None = None


@dataclass(frozen=True, slots=True)
class ViewerNerSelectionResult:
    """Visible and hidden entity spans selected for the document viewer."""

    decisions: tuple[ViewerNerDecision, ...]


    @property
    def visible_candidates(self) -> tuple[NerCandidate, ...]:
        """Return only candidate spans approved for PDF highlighting."""

        return tuple(decision.candidate for decision in self.decisions if decision.is_visible)


    @property
    def hidden_candidates(self) -> tuple[NerCandidate, ...]:
        """Return candidates suppressed by the display overlap policy."""

        return tuple(decision.candidate for decision in self.decisions if not decision.is_visible)


    @property
    def visible_count(self) -> int:
        """Count entity candidates selected for display."""

        return len(self.visible_candidates)


    @property
    def hidden_count(self) -> int:
        """Count entity candidates suppressed from display."""

        return len(self.hidden_candidates)
