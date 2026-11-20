from uuid import uuid4
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AiRuntimeConfigModel, AnalysisModel, ExtractionSchemaVersionModel
from app.pipeline.ner_models import NerCandidate
from app.pipeline.page_mapping_models import MappedNerOccurrence, NerPageMappingResult
from app.repositories.document_repository import DocumentRepository
from app.repositories.entity_occurrence_repository import EntityOccurrenceRepository
from app.services.entity_occurrence_persistence_service import EntityOccurrencePersistenceService


def make_analysis(db_session: Session, user_factory) -> AnalysisModel:
    user = user_factory()

    document = DocumentRepository(db_session).create(
        owner_user_id=user.id,
        original_name="document.pdf",
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
def test_entity_occurrence_is_persisted(db_session: Session, user_factory) -> None:
    analysis = make_analysis(db_session, user_factory)

    occurrence = MappedNerOccurrence(
        candidate=NerCandidate(
            label="ENTE_TEST",
            text="Comune di Palermo",
            start=120,
            end=138,
            confidence=0.9473,
        ),
        page_number=2,
        page_start=30,
        page_end=48,
        is_visible=True,
    )

    mapping = NerPageMappingResult(mapped=(occurrence,), rejected=())

    EntityOccurrencePersistenceService(db_session).persist(
        analysis_id=analysis.id,
        mapping=mapping,
    )

    persisted = EntityOccurrenceRepository(db_session).list_for_analysis(analysis.id)

    assert len(persisted) == 1

    entity = persisted[0]

    assert entity.analysis_id == analysis.id
    assert entity.label == "ENTE_TEST"
    assert entity.text == "Comune di Palermo"
    assert float(entity.confidence) == pytest.approx(0.9473)
    assert entity.global_start == 120
    assert entity.global_end == 138
    assert entity.page == 2
    assert entity.page_start == 30
    assert entity.page_end == 48
    assert entity.is_visible is True


@pytest.mark.integration
def test_hidden_entity_occurrence_is_persisted(db_session: Session, user_factory) -> None:
    analysis = make_analysis(db_session, user_factory)

    occurrence = MappedNerOccurrence(
        candidate=NerCandidate(
            label="LOCALITA",
            text="Palermo",
            start=130,
            end=137,
            confidence=0.90,
        ),
        page_number=2,
        page_start=40,
        page_end=47,
        is_visible=False,
    )

    mapping = NerPageMappingResult(mapped=(occurrence,), rejected=())

    EntityOccurrencePersistenceService(db_session).persist(
        analysis_id=analysis.id,
        mapping=mapping,
    )

    persisted = EntityOccurrenceRepository(db_session).list_for_analysis(analysis.id)

    assert len(persisted) == 1
    assert persisted[0].label == "LOCALITA"
    assert persisted[0].is_visible is False


@pytest.mark.integration
def test_entity_label_is_persisted_as_snapshot(db_session: Session, user_factory) -> None:
    analysis = make_analysis(db_session, user_factory)

    mapping = NerPageMappingResult(
        mapped=(
            MappedNerOccurrence(
                candidate=NerCandidate(
                    label="LABEL_SNAPSHOT_TEST",
                    text="Palermo",
                    start=100,
                    end=107,
                    confidence=0.88,
                ),
                page_number=1,
                page_start=100,
                page_end=107,
                is_visible=True,
            ),
        ),
        rejected=(),
    )

    EntityOccurrencePersistenceService(db_session).persist(
        analysis_id=analysis.id,
        mapping=mapping,
    )

    entity = EntityOccurrenceRepository(db_session).list_for_analysis(analysis.id)[0]

    assert entity.label == "LABEL_SNAPSHOT_TEST"


@pytest.mark.integration
def test_persistence_replaces_previous_occurrences(db_session: Session, user_factory) -> None:
    analysis = make_analysis(db_session, user_factory)
    service = EntityOccurrencePersistenceService(db_session)

    first = NerPageMappingResult(
        mapped=(
            MappedNerOccurrence(
                candidate=NerCandidate(
                    label="FIRST",
                    text="AAA",
                    start=0,
                    end=3,
                    confidence=0.8,
                ),
                page_number=1,
                page_start=0,
                page_end=3,
                is_visible=True,
            ),
        ),
        rejected=(),
    )

    second = NerPageMappingResult(
        mapped=(
            MappedNerOccurrence(
                candidate=NerCandidate(
                    label="SECOND",
                    text="BBB",
                    start=10,
                    end=13,
                    confidence=0.9,
                ),
                page_number=1,
                page_start=10,
                page_end=13,
                is_visible=True,
            ),
        ),
        rejected=(),
    )

    service.persist(analysis_id=analysis.id, mapping=first)
    service.persist(analysis_id=analysis.id, mapping=second)

    persisted = EntityOccurrenceRepository(db_session).list_for_analysis(analysis.id)

    assert len(persisted) == 1
    assert persisted[0].label == "SECOND"


from app.pipeline.page_mapping_models import RejectedNerCandidate, SpanMappingFailureReason


@pytest.mark.integration
def test_rejected_ner_candidate_is_not_persisted(db_session: Session, user_factory) -> None:
    analysis = make_analysis(db_session, user_factory)

    candidate = NerCandidate(
        label="TEST",
        text="ABC",
        start=10,
        end=13,
        confidence=0.90,
    )

    mapping = NerPageMappingResult(
        mapped=(),
        rejected=(
            RejectedNerCandidate(
                candidate=candidate,
                is_visible=True,
                reason=SpanMappingFailureReason.CROSS_PAGE,
            ),
        ),
    )

    EntityOccurrencePersistenceService(db_session).persist(
        analysis_id=analysis.id,
        mapping=mapping,
    )

    persisted = EntityOccurrenceRepository(db_session).list_for_analysis(analysis.id)

    assert persisted == []