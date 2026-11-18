from numbers import Real
from time import perf_counter
from uuid import UUID

from app.core.exceptions import AiInferenceError
from app.core.logging import get_logger
from app.pipeline.config_models import FieldExtractionDefinition, ResolvedAiConfiguration
from app.pipeline.field_models import StructuredExtractionResult, StructuredFieldCandidate
from app.pipeline.model_provider import LoadedAiModel
from app.pipeline.models import PreparedDocumentText


logger = get_logger("pipeline.fields")


class Gliner2FieldExtractor:
    _RECORD_METADATA_KEYS = frozenset({"confidence"})
    
    def extract(
        self,
        *,
        document_id: UUID,
        document: PreparedDocumentText,
        config: ResolvedAiConfiguration,
        model: LoadedAiModel,
    ) -> StructuredExtractionResult:
        started_at = perf_counter()

        if not config.schema.fields:
            raise AiInferenceError("Lo schema non contiene definizioni per Information Extraction.")

        structures = self._build_structures(config)

        logger.info(
            "FIELD_EXTRACTION | phase=start | document_id=%s | model_id=%s | structure_key=%s | chars=%d | fields=%d | threshold=%.4f | chunk_size=%d | chunk_overlap=%d | batch_size=%d | num_workers=%d | overlap_policy=%s",
            document_id,
            config.runtime.model_id,
            config.schema.structure_key,
            document.total_characters,
            len(config.schema.fields),
            config.runtime.field_threshold,
            config.runtime.chunk_size,
            config.runtime.chunk_overlap,
            config.runtime.batch_size,
            config.runtime.num_workers,
            config.runtime.overlap_policy,
        )

        try:
            inference_started_at = perf_counter()

            logger.info(
                "FIELD_EXTRACTION | phase=inference_start | document_id=%s",
                document_id,
            )

            with model.inference_lock:
                raw_result = model.extractor.extract_json_long(
                    document.text,
                    structures,
                    threshold=config.runtime.field_threshold,
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
                "FIELD_EXTRACTION | phase=inference_complete | document_id=%s | elapsed_ms=%.2f",
                document_id,
                inference_ms,
            )

            result = self._normalize(
                document_id=document_id,
                global_text=document.text,
                raw_result=raw_result,
                config=config,
            )

            elapsed_ms = (perf_counter() - started_at) * 1000

            logger.info(
                "FIELD_EXTRACTION | phase=complete | document_id=%s | records=%d | candidates=%d | missing_fields=%d | elapsed_ms=%.2f",
                document_id,
                result.record_count,
                result.total_candidates,
                len(result.missing_field_keys),
                elapsed_ms,
            )

            for field_key, count in sorted(result.counts_by_field.items()):
                logger.debug(
                    "FIELD_EXTRACTION | phase=field_summary | document_id=%s | field_key=%s | count=%d",
                    document_id,
                    field_key,
                    count,
                )

            return result

        except AiInferenceError:
            raise

        except Exception as exc:
            logger.exception(
                "FIELD_EXTRACTION | phase=failed | document_id=%s | model_id=%s",
                document_id,
                config.runtime.model_id,
            )

            raise AiInferenceError("Errore durante l'Information Extraction.") from exc


    def _build_structures(self, config: ResolvedAiConfiguration) -> dict[str, list[str]]:
        structure_key = config.schema.structure_key.strip()

        if not structure_key:
            raise AiInferenceError("Lo schema non possiede una structure_key valida.")

        field_specs: list[str] = []
        seen_keys: set[str] = set()

        for definition in config.schema.fields:
            field_key = definition.field_key.strip()

            if not field_key:
                raise AiInferenceError("Una definizione field possiede una chiave vuota.")

            if field_key in seen_keys:
                raise AiInferenceError(f"Lo schema contiene il field duplicato {field_key!r}.")

            if "::" in field_key:
                raise AiInferenceError(f"La chiave field {field_key!r} contiene il separatore riservato '::'.")

            if field_key in self._RECORD_METADATA_KEYS:
                raise AiInferenceError(f"La chiave field {field_key!r} è riservata dal motore GLiNER2.")

            seen_keys.add(field_key)
            field_specs.append(self._build_field_spec(definition))

        return {structure_key: field_specs}


    def _normalize_dtype(self, data_type: str) -> str:
        normalized = data_type.strip().lower()

        if normalized in {"str", "string"}:
            return "str"

        if normalized == "list":
            return "list"

        raise AiInferenceError(f"Tipo field non supportato dal motore GLiNER2: {data_type!r}.")


    def _build_field_spec(self, definition: FieldExtractionDefinition) -> str:
        field_key = definition.field_key.strip()
        dtype = self._normalize_dtype(definition.data_type)
        description = definition.description.strip() if definition.description else ""

        if description:
            return f"{field_key}::{dtype}::{description}"

        return f"{field_key}::{dtype}"


    def _normalize(
        self,
        *,
        document_id: UUID,
        global_text: str,
        raw_result: object,
        config: ResolvedAiConfiguration,
    ) -> StructuredExtractionResult:
        logger.debug("FIELD_EXTRACTION | phase=normalization_start | document_id=%s", document_id)

        if not isinstance(raw_result, dict):
            raise AiInferenceError("Il modello IE ha restituito un formato non valido.")

        structure_key = config.schema.structure_key
        raw_records = raw_result.get(structure_key)

        if raw_records is None:
            raw_records = []

        if not isinstance(raw_records, list):
            raise AiInferenceError(f"La struttura IE {structure_key!r} non contiene una lista di record valida.")

        field_definitions = {field.field_key: field for field in config.schema.fields}
        candidates: list[StructuredFieldCandidate] = []

        for record_index, record in enumerate(raw_records):
            if not isinstance(record, dict):
                raise AiInferenceError("Il modello IE ha restituito un record non valido.")

            unknown_fields = set(record) - set(field_definitions) - self._RECORD_METADATA_KEYS

            if unknown_fields:
                raise AiInferenceError(f"Il modello IE ha restituito field non presenti nello schema: {sorted(unknown_fields)!r}.")

            for field_key, raw_value in record.items():
                if field_key in self._RECORD_METADATA_KEYS:
                    continue

                definition = field_definitions[field_key]

                normalized_values = self._normalize_field_value(
                    document_id=document_id,
                    global_text=global_text,
                    field_key=field_key,
                    definition=definition,
                    raw_value=raw_value,
                    record_index=record_index,
                )

                candidates.extend(normalized_values)

        candidates.sort(key=lambda item: (item.field_key, item.start, item.end, -item.confidence))

        result = StructuredExtractionResult(
            candidates=tuple(candidates),
            expected_field_keys=tuple(field.field_key for field in config.schema.fields),
            record_count=len(raw_records),
        )

        logger.debug(
            "FIELD_EXTRACTION | phase=normalization_complete | document_id=%s | records=%d | candidates=%d",
            document_id,
            result.record_count,
            result.total_candidates,
        )

        return result


    def _normalize_field_value(
        self,
        *,
        document_id: UUID,
        global_text: str,
        field_key: str,
        definition: FieldExtractionDefinition,
        raw_value: object,
        record_index: int,
    ) -> list[StructuredFieldCandidate]:
        dtype = self._normalize_dtype(definition.data_type)

        if raw_value is None:
            return []

        if dtype == "str":
            raw_items = [raw_value]
        else:
            if not isinstance(raw_value, list):
                raise AiInferenceError(f"Il field {field_key!r} dovrebbe essere una lista.")

            raw_items = raw_value

        candidates: list[StructuredFieldCandidate] = []

        for item_index, item in enumerate(raw_items):
            candidates.append(
                self._normalize_candidate(
                    document_id=document_id,
                    global_text=global_text,
                    field_key=field_key,
                    item=item,
                    record_index=record_index,
                    item_index=item_index,
                )
            )

        return candidates


    def _normalize_candidate(
        self,
        *,
        document_id: UUID,
        global_text: str,
        field_key: str,
        item: object,
        record_index: int,
        item_index: int,
    ) -> StructuredFieldCandidate:
        if not isinstance(item, dict):
            raise AiInferenceError("Candidato IE in formato non valido.")

        value = item.get("text")
        start = item.get("start")
        end = item.get("end")
        confidence = item.get("confidence")

        if not isinstance(value, str):
            raise AiInferenceError("Candidato IE senza testo valido.")

        if (
            not isinstance(start, int)
            or isinstance(start, bool)
            or not isinstance(end, int)
            or isinstance(end, bool)
        ):
            raise AiInferenceError("Candidato IE con offset non validi.")

        if start < 0 or end <= start or end > len(global_text):
            logger.error(
                "FIELD_EXTRACTION | phase=invalid_span | document_id=%s | field_key=%s | start=%s | end=%s | document_chars=%d",
                document_id,
                field_key,
                start,
                end,
                len(global_text),
            )

            raise AiInferenceError("Il modello IE ha restituito uno span fuori dai limiti del documento.")

        if not isinstance(confidence, Real) or isinstance(confidence, bool):
            raise AiInferenceError("Candidato IE senza confidence valida.")

        confidence_value = float(confidence)

        if not 0.0 <= confidence_value <= 1.0:
            raise AiInferenceError("Confidence IE fuori dall'intervallo [0, 1].")

        reconstructed = global_text[start:end]

        if reconstructed != value:
            logger.error(
                "FIELD_EXTRACTION | phase=span_text_mismatch | document_id=%s | field_key=%s | start=%d | end=%d",
                document_id,
                field_key,
                start,
                end,
            )

            raise AiInferenceError("Lo span IE non corrisponde al testo globale.")

        return StructuredFieldCandidate(
            field_key=field_key,
            value=value,
            start=start,
            end=end,
            confidence=confidence_value,
            record_index=record_index,
            item_index=item_index,
        )