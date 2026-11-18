from time import perf_counter
from uuid import UUID

from app.core.logging import get_logger
from app.pipeline.field_models import StructuredExtractionResult, StructuredFieldCandidate
from app.pipeline.ner_models import NerCandidate, NerExtractionResult


logger = get_logger("pipeline.deduplication")


class CandidateDeduplicator:
    def deduplicate_ner(self, *, document_id: UUID, result: NerExtractionResult) -> NerExtractionResult:
        started_at = perf_counter()

        logger.info(
            "NER_DEDUP | phase=start | document_id=%s | candidates=%d",
            document_id,
            result.total_candidates,
        )

        best_by_key: dict[tuple[str, int, int], NerCandidate] = {}

        for candidate in result.candidates:
            key = (candidate.label, candidate.start, candidate.end)
            current = best_by_key.get(key)

            if current is None:
                best_by_key[key] = candidate
                continue

            logger.debug(
                "NER_DEDUP | phase=duplicate_detected | document_id=%s | label=%s | start=%d | end=%d | current_confidence=%.4f | candidate_confidence=%.4f",
                document_id,
                candidate.label,
                candidate.start,
                candidate.end,
                current.confidence,
                candidate.confidence,
            )

            if candidate.confidence > current.confidence:
                best_by_key[key] = candidate

        candidates = tuple(
            sorted(
                best_by_key.values(),
                key=lambda item: (item.start, item.end, item.label, -item.confidence),
            )
        )

        deduplicated = NerExtractionResult(candidates=candidates)
        removed = result.total_candidates - deduplicated.total_candidates
        elapsed_ms = (perf_counter() - started_at) * 1000

        logger.info(
            "NER_DEDUP | phase=complete | document_id=%s | input=%d | output=%d | removed=%d | elapsed_ms=%.2f",
            document_id,
            result.total_candidates,
            deduplicated.total_candidates,
            removed,
            elapsed_ms,
        )

        return deduplicated


    def deduplicate_fields(
        self,
        *,
        document_id: UUID,
        result: StructuredExtractionResult,
    ) -> StructuredExtractionResult:
        started_at = perf_counter()

        logger.info(
            "FIELD_DEDUP | phase=start | document_id=%s | candidates=%d",
            document_id,
            result.total_candidates,
        )

        best_by_key: dict[tuple[str, str, int, int], StructuredFieldCandidate] = {}

        for candidate in result.candidates:
            key = (candidate.field_key, candidate.value, candidate.start, candidate.end)
            current = best_by_key.get(key)

            if current is None:
                best_by_key[key] = candidate
                continue

            logger.debug(
                "FIELD_DEDUP | phase=duplicate_detected | document_id=%s | field_key=%s | start=%d | end=%d | current_confidence=%.4f | candidate_confidence=%.4f",
                document_id,
                candidate.field_key,
                candidate.start,
                candidate.end,
                current.confidence,
                candidate.confidence,
            )

            if candidate.confidence > current.confidence:
                best_by_key[key] = candidate

        candidates = tuple(
            sorted(
                best_by_key.values(),
                key=lambda item: (item.field_key, item.start, item.end, -item.confidence),
            )
        )

        deduplicated = StructuredExtractionResult(
            candidates=candidates,
            expected_field_keys=result.expected_field_keys,
            record_count=result.record_count,
        )

        removed = result.total_candidates - deduplicated.total_candidates
        elapsed_ms = (perf_counter() - started_at) * 1000

        logger.info(
            "FIELD_DEDUP | phase=complete | document_id=%s | input=%d | output=%d | removed=%d | elapsed_ms=%.2f",
            document_id,
            result.total_candidates,
            deduplicated.total_candidates,
            removed,
            elapsed_ms,
        )

        return deduplicated