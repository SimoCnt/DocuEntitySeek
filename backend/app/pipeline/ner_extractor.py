"""Perform GLiNER2 named entity extraction and validate model-provided labels and character spans.
"""

from numbers import Real
from time import perf_counter
from uuid import UUID

from app.core.exceptions import AiInferenceError
from app.core.logging import get_logger
from app.pipeline.config_models import ResolvedAiConfiguration
from app.pipeline.model_provider import LoadedAiModel
from app.pipeline.models import PreparedDocumentText
from app.pipeline.ner_models import NerCandidate, NerExtractionResult


logger = get_logger("pipeline.ner")


class Gliner2NerExtractor:
    """Run GLiNER2 NER and validate labels, scores, and text offsets."""

    def extract(
        self,
        *,
        document_id: UUID,
        document: PreparedDocumentText,
        config: ResolvedAiConfiguration,
        model: LoadedAiModel,
    ) -> NerExtractionResult:
        """Run the configured GLiNER2 NER inference under the model's synchronization lock."""

        started_at = perf_counter()

        if not config.schema.entities:
            raise AiInferenceError("Lo schema non contiene definizioni NER.")

        entity_types = self._build_entity_types(config)

        logger.info(
            "NER | phase=start | document_id=%s | model_id=%s | chars=%d | entity_types=%d | threshold=%.4f | chunk_size=%d | chunk_overlap=%d | batch_size=%d | num_workers=%d | overlap_policy=%s",
            document_id,
            config.runtime.model_id,
            document.total_characters,
            len(entity_types),
            config.runtime.entity_threshold,
            config.runtime.chunk_size,
            config.runtime.chunk_overlap,
            config.runtime.batch_size,
            config.runtime.num_workers,
            config.runtime.overlap_policy,
        )

        try:
            inference_started_at = perf_counter()

            logger.info(
                "NER | phase=inference_start | document_id=%s",
                document_id,
            )

            with model.inference_lock:
                raw_result = model.extractor.extract_entities_long(
                    document.text,
                    entity_types,
                    threshold=config.runtime.entity_threshold,
                    chunk_size=config.runtime.chunk_size,
                    chunk_overlap=config.runtime.chunk_overlap,
                    batch_size=config.runtime.batch_size,
                    num_workers=config.runtime.num_workers,
                    format_results=True,
                    include_confidence=True,
                    include_spans=True,
                    overlap_policy=config.runtime.overlap_policy,
                )

            inference_ms = (perf_counter() - inference_started_at) * 1000

            logger.info(
                "NER | phase=inference_complete | document_id=%s | elapsed_ms=%.2f",
                document_id,
                inference_ms,
            )

            result = self._normalize(
                document_id=document_id,
                global_text=document.text,
                raw_result=raw_result,
                allowed_labels=set(entity_types),
            )

            elapsed_ms = (perf_counter() - started_at) * 1000

            logger.info(
                "NER | phase=complete | document_id=%s | candidates=%d | elapsed_ms=%.2f",
                document_id,
                result.total_candidates,
                elapsed_ms,
            )

            for label, count in sorted(result.counts_by_label.items()):
                logger.debug(
                    "NER | phase=label_summary | document_id=%s | label=%s | count=%d",
                    document_id,
                    label,
                    count,
                )

            return result

        except AiInferenceError:
            raise

        except Exception as exc:
            logger.exception(
                "NER | phase=failed | document_id=%s | model_id=%s",
                document_id,
                config.runtime.model_id,
            )

            raise AiInferenceError("Errore durante l'estrazione NER.") from exc


    def _build_entity_types(self, config: ResolvedAiConfiguration) -> dict[str, str]:
        """Build label/description definitions passed to the NER model."""

        entity_types: dict[str, str] = {}

        for definition in config.schema.entities:
            label = definition.label.strip()

            if not label:
                raise AiInferenceError("Una definizione NER possiede una label vuota.")

            if label in entity_types:
                raise AiInferenceError(f"Lo schema contiene la label NER duplicata {label!r}.")

            description = definition.description.strip() if definition.description else label
            entity_types[label] = description or label

        return entity_types


    def _normalize(
        self,
        *,
        document_id: UUID,
        global_text: str,
        raw_result: object,
        allowed_labels: set[str],
    ) -> NerExtractionResult:
        """Convert raw GLiNER2 output into validated, typed NER candidates."""

        logger.debug(
            "NER | phase=normalization_start | document_id=%s", document_id)

        if not isinstance(raw_result, dict):
            raise AiInferenceError("Il modello NER ha restituito un formato non valido.")

        raw_entities = raw_result.get("entities")

        if not isinstance(raw_entities, dict):
            raise AiInferenceError("La risposta NER non contiene una mappa 'entities' valida.")

        candidates: list[NerCandidate] = []

        for label, items in raw_entities.items():
            if label not in allowed_labels:
                raise AiInferenceError(f"Il modello ha restituito una label non presente nello schema: {label!r}.")

            if not isinstance(items, list):
                raise AiInferenceError(f"La risposta NER per {label!r} non è una lista.")

            for item in items:
                candidate = self._normalize_candidate(
                    document_id=document_id,
                    global_text=global_text,
                    label=label,
                    item=item,
                )

                candidates.append(candidate)

        candidates.sort(key=lambda item: (item.start, item.end, item.label, -item.confidence))
        result = NerExtractionResult(candidates=tuple(candidates))

        logger.debug(
            "NER | phase=normalization_complete | document_id=%s | candidates=%d",
            document_id,
            result.total_candidates,
        )

        return result


    def _normalize_candidate(
        self,
        *,
        document_id: UUID,
        global_text: str,
        label: str,
        item: object,
    ) -> NerCandidate:
        """Validate a candidate's score, label, exact text, and character offsets."""

        if not isinstance(item, dict):
            raise AiInferenceError("Candidato NER in formato non valido.")

        entity_text = item.get("text")
        start = item.get("start")
        end = item.get("end")
        confidence = item.get("confidence")

        if not isinstance(entity_text, str):
            raise AiInferenceError("Candidato NER senza testo valido.")

        if (
            not isinstance(start, int)
            or isinstance(start, bool)
            or not isinstance(end, int)
            or isinstance(end, bool)
        ):
            raise AiInferenceError("Candidato NER con offset non validi.")

        if start < 0 or end <= start or end > len(global_text):
            logger.error(
                "NER | phase=invalid_span | document_id=%s | label=%s | start=%s | end=%s | document_chars=%d",
                document_id,
                label,
                start,
                end,
                len(global_text),
            )

            raise AiInferenceError("Il modello ha restituito uno span NER fuori dai limiti del documento.")

        if not isinstance(confidence, Real) or isinstance(confidence, bool):
            raise AiInferenceError("Candidato NER senza confidence valida.")

        confidence_value = float(confidence)

        if not 0.0 <= confidence_value <= 1.0:
            raise AiInferenceError("Confidence NER fuori dall'intervallo [0, 1].")

        reconstructed = global_text[start:end]

        if reconstructed != entity_text:
            logger.error(
                "NER | phase=span_text_mismatch | document_id=%s | label=%s | start=%d | end=%d",
                document_id,
                label,
                start,
                end,
            )

            raise AiInferenceError("Lo span NER non corrisponde al testo globale.")

        return NerCandidate(
            label=label,
            text=entity_text,
            start=start,
            end=end,
            confidence=confidence_value,
        )
