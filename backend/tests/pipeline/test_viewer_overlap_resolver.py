from uuid import uuid4
import pytest

from app.pipeline.ner_models import NerCandidate, NerExtractionResult
from app.pipeline.viewer_overlap_resolver import ViewerOverlapResolver


@pytest.mark.unit
def test_higher_confidence_wins_overlap() -> None:
    result = NerExtractionResult(
        candidates=(
            NerCandidate(label="A", text="abcdefghij", start=0, end=10, confidence=0.70),
            NerCandidate(label="B", text="defgh", start=3, end=8, confidence=0.95),
        )
    )

    selection = ViewerOverlapResolver().resolve(
        document_id=uuid4(),
        result=result,
    )

    assert selection.visible_count == 1
    assert selection.hidden_count == 1
    assert selection.visible_candidates[0].label == "B"


@pytest.mark.unit
def test_longer_span_wins_when_confidence_is_equal() -> None:
    result = NerExtractionResult(
        candidates=(
            NerCandidate(label="A", text="abcdefghij", start=0, end=10, confidence=0.90),
            NerCandidate(label="B", text="defg", start=3, end=7, confidence=0.90),
        )
    )

    selection = ViewerOverlapResolver().resolve(
        document_id=uuid4(),
        result=result,
    )

    assert selection.visible_candidates[0].label == "A"


@pytest.mark.unit
def test_earlier_start_wins_when_confidence_and_length_are_equal() -> None:
    result = NerExtractionResult(
        candidates=(
            NerCandidate(label="A", text="abcde", start=0, end=5, confidence=0.90),
            NerCandidate(label="B", text="defgh", start=3, end=8, confidence=0.90),
        )
    )

    selection = ViewerOverlapResolver().resolve(
        document_id=uuid4(),
        result=result,
    )

    assert selection.visible_candidates[0].label == "A"


@pytest.mark.unit
def test_adjacent_spans_are_both_visible() -> None:
    result = NerExtractionResult(
        candidates=(
            NerCandidate(label="A", text="abcde", start=0, end=5, confidence=0.90),
            NerCandidate(label="B", text="fghij", start=5, end=10, confidence=0.80),
        )
    )

    selection = ViewerOverlapResolver().resolve(
        document_id=uuid4(),
        result=result,
    )

    assert selection.visible_count == 2
    assert selection.hidden_count == 0


@pytest.mark.unit
def test_hidden_candidate_is_not_discarded() -> None:
    result = NerExtractionResult(
        candidates=(
            NerCandidate(label="A", text="abcdefghij", start=0, end=10, confidence=0.95),
            NerCandidate(label="B", text="defg", start=3, end=7, confidence=0.80),
        )
    )

    selection = ViewerOverlapResolver().resolve(
        document_id=uuid4(),
        result=result,
    )

    assert len(selection.decisions) == 2

    hidden = next(decision for decision in selection.decisions if not decision.is_visible)

    assert hidden.candidate.label == "B"
    assert hidden.blocked_by is not None
    assert hidden.blocked_by.label == "A"


@pytest.mark.unit
def test_greedy_priority_prefers_highest_confidence_even_if_two_smaller_spans_fit() -> None:
    result = NerExtractionResult(
        candidates=(
            NerCandidate(label="A", text="abcdefghijklmnopqrst", start=0, end=20, confidence=0.95),
            NerCandidate(label="B", text="abcdefgh", start=0, end=8, confidence=0.94),
            NerCandidate(label="C", text="mnopqrst", start=12, end=20, confidence=0.93),
        )
    )

    selection = ViewerOverlapResolver().resolve(
        document_id=uuid4(),
        result=result,
    )

    assert [candidate.label for candidate in selection.visible_candidates] == ["A"]
    assert selection.hidden_count == 2


@pytest.mark.unit
def test_exact_tie_is_resolved_deterministically_by_label() -> None:
    result = NerExtractionResult(
        candidates=(
            NerCandidate(label="Z_LABEL", text="Palermo", start=100, end=107, confidence=0.90),
            NerCandidate(label="A_LABEL", text="Palermo", start=100, end=107, confidence=0.90),
        )
    )

    selection = ViewerOverlapResolver().resolve(
        document_id=uuid4(),
        result=result,
    )

    assert selection.visible_candidates[0].label == "A_LABEL"