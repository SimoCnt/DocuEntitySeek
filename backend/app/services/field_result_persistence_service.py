from collections import Counter
from time import perf_counter
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.models import ExtractedFieldModel
from app.pipeline.field_resolution_models import FieldResolutionResult
from app.repositories.extracted_field_repository import ExtractedFieldRepository


logger = get_logger("pipeline.field_persistence")


class FieldResultPersistenceService:
    def __init__(self, session: Session) -> None:
        self.repository = ExtractedFieldRepository(session)
        

    def persist(self, *, analysis_id: UUID, result: FieldResolutionResult) -> list[ExtractedFieldModel]:
        started_at = perf_counter()
        status_counts = Counter(field.status.value for field in result.fields)

        logger.info(
            "FIELD_PERSISTENCE | phase=start | analysis_id=%s | fields=%d | candidates=%d | extracted=%d | ambiguous=%d | not_found=%d",
            analysis_id,
            result.total_fields,
            result.total_candidates,
            status_counts.get("EXTRACTED", 0),
            status_counts.get("AMBIGUOUS", 0),
            status_counts.get("NOT_FOUND", 0),
        )

        models = self.repository.replace_for_analysis(
            analysis_id=analysis_id,
            result=result,
        )

        elapsed_ms = (perf_counter() - started_at) * 1000

        logger.info(
            "FIELD_PERSISTENCE | phase=complete | analysis_id=%s | persisted_fields=%d | persisted_candidates=%d | elapsed_ms=%.2f",
            analysis_id,
            len(models),
            result.total_candidates,
            elapsed_ms,
        )

        return models