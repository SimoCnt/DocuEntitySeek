"""Orchestrate document preparation, GLiNER2 inference, provenance mapping, and result persistence.
"""

from time import perf_counter
from uuid import UUID

from app.core.logging import get_logger
from app.pipeline.candidate_deduplicator import CandidateDeduplicator
from app.pipeline.config_models import ResolvedAiConfiguration
from app.pipeline.field_extractor import Gliner2FieldExtractor
from app.pipeline.field_resolution_models import FieldResolutionResult
from app.pipeline.field_result_resolver import FieldResultResolver
from app.pipeline.model_provider import AiModelProvider
from app.pipeline.ner_extractor import Gliner2NerExtractor
from app.pipeline.ner_models import NerExtractionResult, ViewerNerSelectionResult
from app.pipeline.page_mapping_models import FieldPageMappingResult, NerPageMappingResult
from app.pipeline.page_span_mapper import PageSpanMapper
from app.pipeline.pipeline_models import AiPipelineExecutionResult
from app.pipeline.viewer_overlap_resolver import ViewerOverlapResolver
from app.services.document_preparation_service import DocumentPreparationService
from app.services.entity_occurrence_persistence_service import EntityOccurrencePersistenceService
from app.services.field_result_persistence_service import FieldResultPersistenceService


logger = get_logger("pipeline")


class AnalysisPipeline:
    """Coordinate the end-to-end, synchronous document intelligence pipeline."""

    def __init__(
        self,
        *,
        preparation_service: DocumentPreparationService,
        model_provider: AiModelProvider,
        ner_extractor: Gliner2NerExtractor,
        field_extractor: Gliner2FieldExtractor,
        deduplicator: CandidateDeduplicator,
        overlap_resolver: ViewerOverlapResolver,
        page_mapper: PageSpanMapper,
        field_resolver: FieldResultResolver,
        entity_persistence: EntityOccurrencePersistenceService,
        field_persistence: FieldResultPersistenceService,
    ) -> None:
        self.preparation_service = preparation_service
        self.model_provider = model_provider
        self.ner_extractor = ner_extractor
        self.field_extractor = field_extractor
        self.deduplicator = deduplicator
        self.overlap_resolver = overlap_resolver
        self.page_mapper = page_mapper
        self.field_resolver = field_resolver
        self.entity_persistence = entity_persistence
        self.field_persistence = field_persistence


    def execute(
        self,
        *,
        analysis_id: UUID,
        document_id: UUID,
        owner_user_id: UUID,
        config: ResolvedAiConfiguration,
    ) -> AiPipelineExecutionResult:
        """Execute the complete PDF-to-structured-results workflow.

        Prepares a stable text representation, gets the configured model, runs
        NER and field extraction, resolves text provenance, and persists the
        mapped results in the caller's transaction.
        """

        started_at = perf_counter()

        logger.info(
            "AI_PIPELINE | phase=start | analysis_id=%s | document_id=%s | runtime_config_id=%s | schema_version_id=%s | engine=%s | model_id=%s",
            analysis_id,
            document_id,
            config.runtime.id,
            config.schema.version_id,
            config.runtime.engine,
            config.runtime.model_id,
        )

        prepared = self._prepare_document(
            analysis_id=analysis_id,
            document_id=document_id,
            owner_user_id=owner_user_id,
        )

        model = self._get_model(analysis_id=analysis_id, config=config)

        ner_mapping = self._run_ner(
            analysis_id=analysis_id,
            document_id=document_id,
            prepared=prepared,
            config=config,
            model=model,
        )

        field_resolution, field_mapping = self._run_fields(
            analysis_id=analysis_id,
            document_id=document_id,
            prepared=prepared,
            config=config,
            model=model,
        )

        self._persist_results(
            analysis_id=analysis_id,
            ner_mapping=ner_mapping,
            field_resolution=field_resolution,
        )

        elapsed_ms = (perf_counter() - started_at) * 1000
        visible_entities = sum(occurrence.is_visible for occurrence in ner_mapping.mapped)

        result = AiPipelineExecutionResult(
            runtime_config_id=config.runtime.id,
            schema_version_id=config.schema.version_id,
            page_count=prepared.page_count,
            document_characters=prepared.total_characters,
            entity_count=ner_mapping.mapped_count,
            visible_entity_count=visible_entities,
            hidden_entity_count=ner_mapping.mapped_count - visible_entities,
            rejected_entity_count=ner_mapping.rejected_count,
            field_count=field_resolution.total_fields,
            field_candidate_count=field_resolution.total_candidates,
            extracted_field_count=field_resolution.extracted_count,
            ambiguous_field_count=field_resolution.ambiguous_count,
            not_found_field_count=field_resolution.not_found_count,
            rejected_field_candidate_count=field_mapping.rejected_count,
            elapsed_ms=elapsed_ms,
        )

        logger.info(
            "AI_PIPELINE | phase=complete | analysis_id=%s | document_id=%s | pages=%d | chars=%d | entities=%d | visible_entities=%d | hidden_entities=%d | rejected_entities=%d | fields=%d | field_candidates=%d | extracted_fields=%d | ambiguous_fields=%d | not_found_fields=%d | rejected_field_candidates=%d | elapsed_ms=%.2f",
            analysis_id,
            document_id,
            result.page_count,
            result.document_characters,
            result.entity_count,
            result.visible_entity_count,
            result.hidden_entity_count,
            result.rejected_entity_count,
            result.field_count,
            result.field_candidate_count,
            result.extracted_field_count,
            result.ambiguous_field_count,
            result.not_found_field_count,
            result.rejected_field_candidate_count,
            result.elapsed_ms,
        )

        return result


    def _prepare_document(
            self, 
            *, 
            analysis_id: UUID, 
            document_id: UUID, 
            owner_user_id: UUID
            ):
        """Load the owner's PDF and construct the page-aware analysis input."""

        logger.info(
            "AI_PIPELINE | phase=document_preparation_start | analysis_id=%s | document_id=%s",
            analysis_id,
            document_id,
        )

        prepared = self.preparation_service.prepare(document_id=document_id, owner_user_id=owner_user_id)

        logger.info(
            "AI_PIPELINE | phase=document_preparation_complete | analysis_id=%s | document_id=%s | pages=%d | chars=%d",
            analysis_id,
            document_id,
            prepared.page_count,
            prepared.total_characters,
        )

        return prepared


    def _get_model(
            self, 
            *, 
            analysis_id: UUID, 
            config: ResolvedAiConfiguration
            ):
        """Retrieve a cached compatible GLiNER2 model for the selected runtime."""

        logger.info(
            "AI_PIPELINE | phase=model_start | analysis_id=%s | model_id=%s",
            analysis_id,
            config.runtime.model_id,
        )

        model = self.model_provider.get_model(config.runtime)

        logger.info(
            "AI_PIPELINE | phase=model_complete | analysis_id=%s | model_id=%s",
            analysis_id,
            config.runtime.model_id,
        )

        return model


    def _run_ner(
        self,
        *,
        analysis_id: UUID,
        document_id: UUID,
        prepared,
        config: ResolvedAiConfiguration,
        model,
    ) -> NerPageMappingResult:
        """Extract, deduplicate, resolve overlap, map, and persist named entities."""

        logger.info(
            "AI_PIPELINE | phase=ner_start | analysis_id=%s | document_id=%s | entity_definitions=%d",
            analysis_id,
            document_id,
            len(config.schema.entities),
        )

        if not config.schema.entities:
            logger.info(
                "AI_PIPELINE | phase=ner_skipped | analysis_id=%s | reason=no_entity_definitions",
                analysis_id,
            )

            return NerPageMappingResult(mapped=(), rejected=())

        result = self.ner_extractor.extract(
            document_id=document_id,
            document=prepared,
            config=config,
            model=model,
        )

        logger.info(
            "AI_PIPELINE | phase=ner_extracted | analysis_id=%s | candidates=%d",
            analysis_id,
            result.total_candidates,
        )

        result = self.deduplicator.deduplicate_ner(document_id=document_id, result=result)

        viewer = self.overlap_resolver.resolve(document_id=document_id, result=result)

        mapping = self.page_mapper.map_ner(
            document_id=document_id,
            document=prepared,
            selection=viewer,
        )

        logger.info(
            "AI_PIPELINE | phase=ner_complete | analysis_id=%s | mapped=%d | rejected=%d",
            analysis_id,
            mapping.mapped_count,
            mapping.rejected_count,
        )

        return mapping


    def _run_fields(
        self,
        *,
        analysis_id: UUID,
        document_id: UUID,
        prepared,
        config: ResolvedAiConfiguration,
        model,
    ) -> tuple[FieldResolutionResult, FieldPageMappingResult]:
        """Extract structured fields, map candidate spans, and resolve final values."""

        logger.info(
            "AI_PIPELINE | phase=field_extraction_start | analysis_id=%s | document_id=%s | field_definitions=%d",
            analysis_id,
            document_id,
            len(config.schema.fields),
        )

        if not config.schema.fields:
            logger.info("AI_PIPELINE | phase=field_extraction_skipped | analysis_id=%s | reason=no_field_definitions", analysis_id)

            return (
                FieldResolutionResult(fields=()),
                FieldPageMappingResult(mapped=(), rejected=()),
            )

        extraction = self.field_extractor.extract(
            document_id=document_id,
            document=prepared,
            config=config,
            model=model,
        )

        logger.info(
            "AI_PIPELINE | phase=fields_extracted | analysis_id=%s | candidates=%d",
            analysis_id,
            extraction.total_candidates,
        )

        extraction = self.deduplicator.deduplicate_fields(document_id=document_id, result=extraction)

        mapping = self.page_mapper.map_fields(
            document_id=document_id,
            document=prepared,
            result=extraction,
        )

        resolution = self.field_resolver.resolve(
            document_id=document_id,
            config=config,
            mapping=mapping,
        )

        logger.info(
            "AI_PIPELINE | phase=field_extraction_complete | analysis_id=%s | fields=%d | extracted=%d | ambiguous=%d | not_found=%d",
            analysis_id,
            resolution.total_fields,
            resolution.extracted_count,
            resolution.ambiguous_count,
            resolution.not_found_count,
        )

        return resolution, mapping


    def _persist_results(
        self,
        *,
        analysis_id: UUID,
        ner_mapping: NerPageMappingResult,
        field_resolution: FieldResolutionResult,
    ) -> None:
        """Persist page-mapped entities and resolved fields within the active database transaction.
        """

        logger.info("AI_PIPELINE | phase=persistence_start | analysis_id=%s", analysis_id)
        self.entity_persistence.persist(analysis_id=analysis_id, mapping=ner_mapping)
        self.field_persistence.persist(analysis_id=analysis_id, result=field_resolution)
        logger.info("AI_PIPELINE | phase=persistence_complete | analysis_id=%s", analysis_id)
