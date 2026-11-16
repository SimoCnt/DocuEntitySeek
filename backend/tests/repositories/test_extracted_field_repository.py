from sqlalchemy import select
import pytest
from sqlalchemy.orm import Session

from app.db.models import AiRuntimeConfigModel, AnalysisModel, ExtractionSchemaVersionModel, FieldCandidateModel
from app.pipeline.field_resolution_models import FieldResolutionResult, FieldStatus, RankedFieldCandidate, ResolvedExtractedField
from app.pipeline.field_models import StructuredFieldCandidate
from app.pipeline.page_mapping_models import SpanMappingFailureReason
from app.repositories.extracted_field_repository import ExtractedFieldRepository
from app.services.field_result_persistence_service import FieldResultPersistenceService
from app.repositories.document_repository import DocumentRepository


def make_analysis(db_session: Session, user_factory) -> AnalysisModel:
    user = user_factory()

    document = DocumentRepository(db_session).create(
        owner_user_id=user.id,
        original_name="document.pdf",
        category="TEST",
        mime_type="application/pdf",
        size_bytes=100,
    )

    schema_version = db_session.scalar(select(ExtractionSchemaVersionModel).limit(1))
    runtime_config = db_session.scalar(
        select(AiRuntimeConfigModel).where(AiRuntimeConfigModel.is_active.is_(True))
    )

    assert schema_version is not None
    assert runtime_config is not None

    analysis = AnalysisModel(
        document_id=document.id,
        schema_version_id=schema_version.id,
        ai_runtime_config_id=runtime_config.id,
        config={},
    )

    db_session.add(analysis)
    db_session.flush()

    return analysis


@pytest.mark.integration
def test_field_and_candidates_are_persisted(db_session, user_factory) -> None:
    analysis = make_analysis(db_session, user_factory)

    best = RankedFieldCandidate(
        candidate=StructuredFieldCandidate(
            field_key="campo_test",
            value="ABC",
            start=100,
            end=103,
            confidence=0.95,
            record_index=0,
            item_index=0,
        ),
        rank=1,
        page_number=1,
    )

    alternative = RankedFieldCandidate(
        candidate=StructuredFieldCandidate(
            field_key="campo_test",
            value="XYZ",
            start=500,
            end=503,
            confidence=0.82,
            record_index=1,
            item_index=0,
        ),
        rank=2,
        page_number=2,
    )

    result = FieldResolutionResult(
        fields=(
            ResolvedExtractedField(
                field_key="campo_test",
                status=FieldStatus.AMBIGUOUS,
                value="ABC",
                confidence=0.95,
                page_number=1,
                global_start=100,
                global_end=103,
                candidates=(best, alternative),
            ),
        )
    )

    FieldResultPersistenceService(db_session).persist(
        analysis_id=analysis.id,
        result=result,
    )

    fields = ExtractedFieldRepository(db_session).list_for_analysis(analysis.id)

    assert len(fields) == 1

    field = fields[0]

    assert field.field_key == "campo_test"
    assert field.status == "AMBIGUOUS"
    assert field.value_text == "ABC"
    assert float(field.confidence) == pytest.approx(0.95)
    assert field.page == 1
    assert field.global_start == 100
    assert field.global_end == 103

    candidates = list(
        db_session.scalars(
            select(FieldCandidateModel)
            .where(FieldCandidateModel.extracted_field_id == field.id)
            .order_by(FieldCandidateModel.candidate_rank)
        ).all()
    )

    assert len(candidates) == 2
    assert candidates[0].candidate_rank == 1
    assert candidates[0].value_text == "ABC"
    assert candidates[1].candidate_rank == 2
    assert candidates[1].value_text == "XYZ"


@pytest.mark.integration
def test_not_found_field_is_persisted_without_value(db_session, user_factory) -> None:
    analysis = make_analysis(db_session, user_factory)

    result = FieldResolutionResult(
        fields=(
            ResolvedExtractedField(
                field_key="campo_mancante",
                status=FieldStatus.NOT_FOUND,
                value=None,
                confidence=None,
                page_number=None,
                global_start=None,
                global_end=None,
                candidates=(),
            ),
        )
    )

    FieldResultPersistenceService(db_session).persist(
        analysis_id=analysis.id,
        result=result,
    )

    field = ExtractedFieldRepository(db_session).list_for_analysis(analysis.id)[0]

    assert field.status == "NOT_FOUND"
    assert field.value_text is None
    assert field.confidence is None
    assert field.page is None
    assert field.global_start is None
    assert field.global_end is None


@pytest.mark.integration
def test_field_and_candidates_are_persisted(db_session, user_factory) -> None:
    analysis = make_analysis(db_session, user_factory)

    best = RankedFieldCandidate(
        candidate=StructuredFieldCandidate(
            field_key="campo_test",
            value="ABC",
            start=100,
            end=103,
            confidence=0.95,
            record_index=0,
            item_index=0,
        ),
        rank=1,
        page_number=1,
    )

    alternative = RankedFieldCandidate(
        candidate=StructuredFieldCandidate(
            field_key="campo_test",
            value="XYZ",
            start=500,
            end=503,
            confidence=0.82,
            record_index=1,
            item_index=0,
        ),
        rank=2,
        page_number=2,
    )

    result = FieldResolutionResult(
        fields=(
            ResolvedExtractedField(
                field_key="campo_test",
                status=FieldStatus.AMBIGUOUS,
                value="ABC",
                confidence=0.95,
                page_number=1,
                global_start=100,
                global_end=103,
                candidates=(best, alternative),
            ),
        )
    )

    FieldResultPersistenceService(db_session).persist(
        analysis_id=analysis.id,
        result=result,
    )

    fields = ExtractedFieldRepository(db_session).list_for_analysis(analysis.id)

    assert len(fields) == 1

    field = fields[0]

    assert field.field_key == "campo_test"
    assert field.status == "AMBIGUOUS"
    assert field.value_text == "ABC"
    assert float(field.confidence) == pytest.approx(0.95)
    assert field.page == 1
    assert field.global_start == 100
    assert field.global_end == 103

    candidates = list(
        db_session.scalars(
            select(FieldCandidateModel)
            .where(FieldCandidateModel.extracted_field_id == field.id)
            .order_by(FieldCandidateModel.candidate_rank)
        ).all()
    )

    assert len(candidates) == 2
    assert candidates[0].candidate_rank == 1
    assert candidates[0].value_text == "ABC"
    assert candidates[1].candidate_rank == 2
    assert candidates[1].value_text == "XYZ"


@pytest.mark.integration
def test_not_found_field_is_persisted_without_value(db_session, user_factory) -> None:
    analysis = make_analysis(db_session, user_factory)

    result = FieldResolutionResult(
        fields=(
            ResolvedExtractedField(
                field_key="campo_mancante",
                status=FieldStatus.NOT_FOUND,
                value=None,
                confidence=None,
                page_number=None,
                global_start=None,
                global_end=None,
                candidates=(),
            ),
        )
    )

    FieldResultPersistenceService(db_session).persist(
        analysis_id=analysis.id,
        result=result,
    )

    field = ExtractedFieldRepository(db_session).list_for_analysis(analysis.id)[0]

    assert field.status == "NOT_FOUND"
    assert field.value_text is None
    assert field.confidence is None
    assert field.page is None
    assert field.global_start is None
    assert field.global_end is None


@pytest.mark.integration
def test_unmapped_candidate_keeps_global_provenance(db_session, user_factory) -> None:
    analysis = make_analysis(db_session, user_factory)

    candidate = RankedFieldCandidate(
        candidate=StructuredFieldCandidate(
            field_key="campo_test",
            value="ABC",
            start=100,
            end=103,
            confidence=0.95,
            record_index=0,
            item_index=0,
        ),
        rank=1,
        page_number=None,
        mapping_failure_reason=SpanMappingFailureReason.CROSS_PAGE,
    )

    result = FieldResolutionResult(
        fields=(
            ResolvedExtractedField(
                field_key="campo_test",
                status=FieldStatus.EXTRACTED,
                value="ABC",
                confidence=0.95,
                page_number=None,
                global_start=100,
                global_end=103,
                candidates=(candidate,),
            ),
        )
    )

    FieldResultPersistenceService(db_session).persist(
        analysis_id=analysis.id,
        result=result,
    )

    field = ExtractedFieldRepository(db_session).list_for_analysis(analysis.id)[0]

    persisted = db_session.scalar(
        select(FieldCandidateModel).where(FieldCandidateModel.extracted_field_id == field.id)
    )

    assert field.page is None
    assert field.global_start == 100
    assert field.global_end == 103

    assert persisted is not None
    assert persisted.page is None
    assert persisted.global_start == 100
    assert persisted.global_end == 103