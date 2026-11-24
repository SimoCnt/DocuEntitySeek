"""Rank and resolve structured field candidates into extracted, ambiguous, or missing values."""

from collections import defaultdict
from time import perf_counter
from uuid import UUID

from app.core.exceptions import AiInferenceError
from app.core.logging import get_logger
from app.pipeline.config_models import ResolvedAiConfiguration
from app.pipeline.field_models import StructuredFieldCandidate
from app.pipeline.field_resolution_models import FieldResolutionResult, FieldStatus, RankedFieldCandidate, ResolvedExtractedField
from app.pipeline.page_mapping_models import FieldPageMappingResult


logger = get_logger("pipeline.field_resolution")


class FieldResultResolver:
    """Rank field candidates and determine final value status per schema field."""

    def resolve(
        self,
        *,
        document_id: UUID,
        config: ResolvedAiConfiguration,
        mapping: FieldPageMappingResult,
    ) -> FieldResolutionResult:
        """Resolve each schema field into a ranked candidate and final extraction status."""

        started_at = perf_counter()

        logger.info(
            "FIELD_RESOLUTION | phase=start | document_id=%s | fields=%d | mapped_candidates=%d | rejected_candidates=%d",
            document_id,
            len(config.schema.fields),
            mapping.mapped_count,
            mapping.rejected_count,
        )

        definitions = {definition.field_key: definition for definition in config.schema.fields}
        candidates_by_field: dict[str, list[RankedFieldCandidate]] = defaultdict(list)

        for mapped in mapping.mapped:
            self._ensure_known_field(mapped.candidate, definitions)

            candidates_by_field[mapped.candidate.field_key].append(
                RankedFieldCandidate(
                    candidate=mapped.candidate,
                    rank=0,
                    page_number=mapped.page_number,
                )
            )

        for rejected in mapping.rejected:
            self._ensure_known_field(rejected.candidate, definitions)

            candidates_by_field[rejected.candidate.field_key].append(
                RankedFieldCandidate(
                    candidate=rejected.candidate,
                    rank=0,
                    page_number=None,
                    mapping_failure_reason=rejected.reason,
                )
            )

        resolved_fields: list[ResolvedExtractedField] = []

        for definition in config.schema.fields:
            candidates = candidates_by_field[definition.field_key]

            resolved = self._resolve_field(
                field_key=definition.field_key,
                candidates=candidates,
            )

            resolved_fields.append(resolved)

            if definition.is_required and resolved.status == FieldStatus.NOT_FOUND:
                logger.warning(
                    "FIELD_RESOLUTION | phase=required_field_not_found | document_id=%s | field_key=%s",
                    document_id,
                    definition.field_key,
                )

        result = FieldResolutionResult(fields=tuple(resolved_fields))
        elapsed_ms = (perf_counter() - started_at) * 1000

        logger.info(
            "FIELD_RESOLUTION | phase=complete | document_id=%s | fields=%d | extracted=%d | ambiguous=%d | not_found=%d | candidates=%d | elapsed_ms=%.2f",
            document_id,
            result.total_fields,
            result.extracted_count,
            result.ambiguous_count,
            result.not_found_count,
            result.total_candidates,
            elapsed_ms,
        )

        return result


    @staticmethod
    def _ensure_known_field(candidate: StructuredFieldCandidate, definitions: dict[str, object]) -> None:
        """Reject candidates whose field key is absent from the selected schema."""

        if candidate.field_key not in definitions:
            raise AiInferenceError(f"Candidato IE associato a un field non presente nello schema: {candidate.field_key!r}.")


    @staticmethod
    def _candidate_sort_key(candidate: RankedFieldCandidate) -> tuple[float, bool, int, int, str, int, int]:
        """Produce a deterministic ordering key for comparable field candidates."""

        value = candidate.candidate

        return (
            -value.confidence,
            not candidate.is_page_mapped,
            value.start,
            value.end,
            value.value,
            value.record_index,
            value.item_index,
        )


    def _resolve_field(self, *, field_key: str, candidates: list[RankedFieldCandidate]) -> ResolvedExtractedField:
        """Determine the selected value and status for one schema field."""

        if not candidates:
            return ResolvedExtractedField(
                field_key=field_key,
                status=FieldStatus.NOT_FOUND,
                value=None,
                confidence=None,
                page_number=None,
                global_start=None,
                global_end=None,
                candidates=(),
            )

        ordered = sorted(candidates, key=self._candidate_sort_key)

        ranked = tuple(
            RankedFieldCandidate(
                candidate=item.candidate,
                rank=index,
                page_number=item.page_number,
                mapping_failure_reason=item.mapping_failure_reason,
            )
            for index, item in enumerate(ordered, start=1)
        )

        distinct_values = {item.candidate.value for item in ranked}
        status = FieldStatus.EXTRACTED if len(distinct_values) == 1 else FieldStatus.AMBIGUOUS
        best = ranked[0]

        return ResolvedExtractedField(
            field_key=field_key,
            status=status,
            value=best.candidate.value,
            confidence=best.candidate.confidence,
            page_number=best.page_number,
            global_start=best.candidate.start,
            global_end=best.candidate.end,
            candidates=ranked,
        )
