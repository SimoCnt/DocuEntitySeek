from uuid import uuid4
import pytest

from app.pipeline.config_models import FieldExtractionDefinition, ResolvedAiConfiguration, ResolvedExtractionSchema, RuntimeAiConfig
from app.pipeline.field_models import StructuredFieldCandidate
from app.pipeline.field_resolution_models import FieldStatus
from app.pipeline.field_result_resolver import FieldResultResolver
from app.pipeline.page_mapping_models import FieldPageMappingResult, MappedFieldCandidate, RejectedFieldCandidate, SpanMappingFailureReason


def make_config(*, required: bool = False) -> ResolvedAiConfiguration:
    runtime = RuntimeAiConfig(
        id=uuid4(),
        name="Test",
        version=1,
        engine="GLINER2",
        model_id="test/model",
        model_revision=None,
        chunk_size=320,
        chunk_overlap=48,
        batch_size=4,
        num_workers=0,
        overlap_policy="allow",
        entity_threshold=0.5,
        field_threshold=0.5,
    )

    schema = ResolvedExtractionSchema(
        schema_id=uuid4(),
        schema_name="Test",
        schema_domain="TEST",
        structure_key="test_structure",
        version_id=uuid4(),
        version=1,
        entities=(),
        fields=(
            FieldExtractionDefinition(
                id=uuid4(),
                field_key="campo_test",
                label="Campo test",
                description="Campo test",
                data_type="str",
                is_required=required,
            ),
        ),
    )

    return ResolvedAiConfiguration(
        runtime=runtime,
        schema=schema,
        text_layout_version="page-join-v1",
    )


@pytest.mark.unit
def test_field_without_candidates_is_not_found() -> None:
    result = FieldResultResolver().resolve(
        document_id=uuid4(),
        config=make_config(),
        mapping=FieldPageMappingResult(mapped=(), rejected=()),
    )

    field = result.fields[0]

    assert field.status == FieldStatus.NOT_FOUND
    assert field.value is None
    assert field.confidence is None
    assert field.candidates == ()


@pytest.mark.unit
def test_same_value_multiple_times_is_extracted_not_ambiguous() -> None:
    candidate_a = StructuredFieldCandidate(
        field_key="campo_test",
        value="ABC",
        start=100,
        end=103,
        confidence=0.80,
        record_index=0,
        item_index=0,
    )

    candidate_b = StructuredFieldCandidate(
        field_key="campo_test",
        value="ABC",
        start=500,
        end=503,
        confidence=0.95,
        record_index=1,
        item_index=0,
    )

    result = FieldResultResolver().resolve(
        document_id=uuid4(),
        config=make_config(),
        mapping=FieldPageMappingResult(
            mapped=(
                MappedFieldCandidate(candidate=candidate_a, page_number=1, page_start=100, page_end=103),
                MappedFieldCandidate(candidate=candidate_b, page_number=2, page_start=40, page_end=43),
            ),
            rejected=(),
        ),
    )

    field = result.fields[0]

    assert field.status == FieldStatus.EXTRACTED
    assert field.value == "ABC"
    assert field.confidence == pytest.approx(0.95)
    assert len(field.candidates) == 2
    assert field.candidates[0].rank == 1
    assert field.candidates[0].candidate is candidate_b


@pytest.mark.unit
def test_distinct_values_make_field_ambiguous() -> None:
    result = FieldResultResolver().resolve(
        document_id=uuid4(),
        config=make_config(),
        mapping=FieldPageMappingResult(
            mapped=(
                MappedFieldCandidate(
                    candidate=StructuredFieldCandidate(
                        field_key="campo_test",
                        value="ABC",
                        start=100,
                        end=103,
                        confidence=0.96,
                        record_index=0,
                        item_index=0,
                    ),
                    page_number=1,
                    page_start=100,
                    page_end=103,
                ),
                MappedFieldCandidate(
                    candidate=StructuredFieldCandidate(
                        field_key="campo_test",
                        value="XYZ",
                        start=500,
                        end=503,
                        confidence=0.83,
                        record_index=1,
                        item_index=0,
                    ),
                    page_number=2,
                    page_start=50,
                    page_end=53,
                ),
            ),
            rejected=(),
        ),
    )

    field = result.fields[0]

    assert field.status == FieldStatus.AMBIGUOUS
    assert field.value == "ABC"
    assert field.confidence == pytest.approx(0.96)
    assert [candidate.candidate.value for candidate in field.candidates] == ["ABC", "XYZ"]


@pytest.mark.unit
def test_unmapped_candidate_is_still_resolved() -> None:
    candidate = StructuredFieldCandidate(
        field_key="campo_test",
        value="ABC",
        start=100,
        end=103,
        confidence=0.97,
        record_index=0,
        item_index=0,
    )

    result = FieldResultResolver().resolve(
        document_id=uuid4(),
        config=make_config(),
        mapping=FieldPageMappingResult(
            mapped=(),
            rejected=(
                RejectedFieldCandidate(
                    candidate=candidate,
                    reason=SpanMappingFailureReason.CROSS_PAGE,
                ),
            ),
        ),
    )

    field = result.fields[0]

    assert field.status == FieldStatus.EXTRACTED
    assert field.value == "ABC"
    assert field.page_number is None
    assert len(field.candidates) == 1
    assert field.candidates[0].page_number is None
    assert field.candidates[0].mapping_failure_reason == SpanMappingFailureReason.CROSS_PAGE