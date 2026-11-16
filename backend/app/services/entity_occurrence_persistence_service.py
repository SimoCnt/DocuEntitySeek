from collections import Counter
from time import perf_counter
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.models import EntityOccurrenceModel
from app.pipeline.page_mapping_models import NerPageMappingResult
from app.repositories.entity_occurrence_repository import EntityOccurrenceRepository


logger = get_logger("pipeline.entity_persistence")


class EntityOccurrencePersistenceService:
    def __init__(self, session: Session) -> None:
        self.repository = EntityOccurrenceRepository(session)
        

    def persist(self, *, analysis_id: UUID, mapping: NerPageMappingResult) -> list[EntityOccurrenceModel]:
        started_at = perf_counter()

        visible_count = sum(occurrence.is_visible for occurrence in mapping.mapped)
        hidden_count = mapping.mapped_count - visible_count

        logger.info(
            "ENTITY_PERSISTENCE | phase=start | analysis_id=%s | mapped=%d | rejected=%d | visible=%d | hidden=%d",
            analysis_id,
            mapping.mapped_count,
            mapping.rejected_count,
            visible_count,
            hidden_count,
        )

        if mapping.rejected:
            rejection_counts = Counter(rejected.reason.value for rejected in mapping.rejected)

            for reason, count in sorted(rejection_counts.items()):
                logger.warning(
                    "ENTITY_PERSISTENCE | phase=rejected_not_persisted | analysis_id=%s | reason=%s | count=%d",
                    analysis_id,
                    reason,
                    count,
                )

        models = self.repository.replace_for_analysis(
            analysis_id=analysis_id,
            occurrences=mapping.mapped,
        )

        elapsed_ms = (perf_counter() - started_at) * 1000

        logger.info(
            "ENTITY_PERSISTENCE | phase=complete | analysis_id=%s | persisted=%d | elapsed_ms=%.2f",
            analysis_id,
            len(models),
            elapsed_ms,
        )

        return models