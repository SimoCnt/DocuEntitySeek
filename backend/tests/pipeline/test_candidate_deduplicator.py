from uuid import uuid4
import pytest

from app.pipeline.candidate_deduplicator import CandidateDeduplicator
from app.pipeline.field_models import StructuredExtractionResult, StructuredFieldCandidate
from app.pipeline.ner_models import NerCandidate, NerExtractionResult


@pytest.mark.unit
def test_ner_duplicate_keeps_highest_confidence() -> None:
    result = NerExtractionResult(
        candidates=(
            NerCandidate(label="ENTE_TEST", text="Comune di Palermo", start=100, end=118, confidence=0.72),
            NerCandidate(label="ENTE_TEST", text="Comune di Palermo", start=100, end=118, confidence=0.94),
        )
    )

    deduplicated = CandidateDeduplicator().deduplicate_ner(
        document_id=uuid4(),
        result=result,
    )

    assert deduplicated.total_candidates == 1
    assert deduplicated.candidates[0].confidence == pytest.approx(0.94)


@pytest.mark.unit
def test_ner_same_text_at_different_positions_is_preserved() -> None:
    result = NerExtractionResult(
        candidates=(
            NerCandidate(label="ENTE_TEST", text="Comune di Palermo", start=100, end=118, confidence=0.91),
            NerCandidate(label="ENTE_TEST", text="Comune di Palermo", start=5000, end=5018, confidence=0.89),
        )
    )

    deduplicated = CandidateDeduplicator().deduplicate_ner(
        document_id=uuid4(),
        result=result,
    )

    assert deduplicated.total_candidates == 2


@pytest.mark.unit
def test_ner_different_labels_on_same_span_are_preserved() -> None:
    result = NerExtractionResult(
        candidates=(
            NerCandidate(
                label="LOCALITA",
                text="Palermo",
                start=100,
                end=107,
                confidence=0.91,
            ),
            NerCandidate(
                label="ORGANIZZAZIONE",
                text="Palermo",
                start=100,
                end=107,
                confidence=0.76,
            ),
        )
    )

    deduplicated = CandidateDeduplicator().deduplicate_ner(
        document_id=uuid4(),
        result=result,
    )

    assert deduplicated.total_candidates == 2


@pytest.mark.unit
def test_field_duplicate_keeps_highest_confidence() -> None:
    result = StructuredExtractionResult(
        candidates=(
            StructuredFieldCandidate(
                field_key="campo_test",
                value="Comune di Palermo",
                start=100,
                end=118,
                confidence=0.74,
                record_index=0,
                item_index=0,
            ),
            StructuredFieldCandidate(
                field_key="campo_test",
                value="Comune di Palermo",
                start=100,
                end=118,
                confidence=0.96,
                record_index=1,
                item_index=0,
            ),
        ),
        expected_field_keys=("campo_test",),
        record_count=2,
    )

    deduplicated = CandidateDeduplicator().deduplicate_fields(
        document_id=uuid4(),
        result=result,
    )

    assert deduplicated.total_candidates == 1
    assert deduplicated.candidates[0].confidence == pytest.approx(0.96)


@pytest.mark.unit
def test_field_same_value_at_different_positions_is_preserved() -> None:
    result = StructuredExtractionResult(
        candidates=(
            StructuredFieldCandidate(
                field_key="campo_test",
                value="A123",
                start=100,
                end=104,
                confidence=0.90,
                record_index=0,
                item_index=0,
            ),
            StructuredFieldCandidate(
                field_key="campo_test",
                value="A123",
                start=5000,
                end=5004,
                confidence=0.87,
                record_index=1,
                item_index=0,
            ),
        ),
        expected_field_keys=("campo_test",),
        record_count=2,
    )

    deduplicated = CandidateDeduplicator().deduplicate_fields(
        document_id=uuid4(),
        result=result,
    )

    assert deduplicated.total_candidates == 2


@pytest.mark.unit
def test_ner_result_is_sorted_deterministically() -> None:
    result = NerExtractionResult(
        candidates=(
            NerCandidate(label="B", text="Secondo", start=100, end=107, confidence=0.80),
            NerCandidate(label="A", text="Primo", start=10, end=15, confidence=0.90),
        )
    )

    deduplicated = CandidateDeduplicator().deduplicate_ner(
        document_id=uuid4(),
        result=result,
    )

    assert [candidate.start for candidate in deduplicated.candidates] == [10, 100]