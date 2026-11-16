from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import AiConfigurationError
from app.core.logging import get_logger
from app.pipeline.config_models import EntityExtractionDefinition, FieldExtractionDefinition, ResolvedAiConfiguration, ResolvedExtractionSchema, RuntimeAiConfig
from app.pipeline.provenance import TEXT_LAYOUT_VERSION
from app.repositories.ai_runtime_config_repository import AiRuntimeConfigRepository
from app.repositories.extraction_schema_repository import ExtractionSchemaRepository


logger = get_logger("pipeline.config")


class AiConfigurationResolver:
    def __init__(self, session: Session) -> None:
        self.runtime_configs = AiRuntimeConfigRepository(session)
        self.schemas = ExtractionSchemaRepository(session)

    def resolve(self, *, schema_version_id: UUID | None = None) -> ResolvedAiConfiguration:
        logger.info("AI_CONFIG | phase=resolve_start | requested_schema_version_id=%s", schema_version_id)
        runtime_model = self.runtime_configs.get_active()

        if runtime_model is None:
            logger.error("AI_CONFIG | phase=runtime_missing")
            raise AiConfigurationError("Nessuna configurazione AI attiva.")

        logger.info(
            "AI_CONFIG | phase=runtime_loaded | config_id=%s | config_version=%d | engine=%s | model_id=%s | chunk_size=%d | chunk_overlap=%d | batch_size=%d | num_workers=%d | overlap_policy=%s | entity_threshold=%.4f | field_threshold=%.4f",
            runtime_model.id,
            runtime_model.version,
            runtime_model.engine,
            runtime_model.model_id,
            runtime_model.chunk_size,
            runtime_model.chunk_overlap,
            runtime_model.batch_size,
            runtime_model.num_workers,
            runtime_model.overlap_policy,
            float(runtime_model.entity_threshold),
            float(runtime_model.field_threshold),
        )

        if schema_version_id:
            schema_model = self.schemas.get_version(schema_version_id)
        else:
            schema_model = self.schemas.get_default_builtin_version()

        if schema_model is None:
            logger.error("AI_CONFIG | phase=schema_missing | requested_schema_version_id=%s", schema_version_id)
            raise AiConfigurationError("Nessuna versione dello schema di estrazione disponibile.")

        entities = tuple(
            EntityExtractionDefinition(
                id=definition.id,
                label=definition.label,
                description=definition.description,
            )
            for definition in sorted(schema_model.entity_definitions, key=lambda item: item.sort_order)
        )

        fields = tuple(
            FieldExtractionDefinition(
                id=definition.id,
                field_key=definition.field_key,
                label=definition.label,
                description=definition.description,
                data_type=definition.data_type,
                is_required=definition.is_required,
            )
            for definition in sorted(schema_model.field_definitions, key=lambda item: item.sort_order)
        )

        if not entities and not fields:
            logger.error("AI_CONFIG | phase=empty_schema | schema_version_id=%s", schema_model.id)
            raise AiConfigurationError("Lo schema di estrazione non contiene entità né campi.")

        runtime = RuntimeAiConfig(
            id=runtime_model.id,
            name=runtime_model.name,
            version=runtime_model.version,
            engine=runtime_model.engine,
            model_id=runtime_model.model_id,
            model_revision=runtime_model.model_revision,
            chunk_size=runtime_model.chunk_size,
            chunk_overlap=runtime_model.chunk_overlap,
            batch_size=runtime_model.batch_size,
            num_workers=runtime_model.num_workers,
            overlap_policy=runtime_model.overlap_policy,
            entity_threshold=float(runtime_model.entity_threshold),
            field_threshold=float(runtime_model.field_threshold),
        )

        schema = ResolvedExtractionSchema(
            schema_id=schema_model.schema_id,
            structure_key=schema_model.schema.structure_key,
            schema_name=schema_model.schema.name,
            schema_domain=schema_model.schema.domain,
            version_id=schema_model.id,
            version=schema_model.version,
            entities=entities,
            fields=fields,
        )

        resolved = ResolvedAiConfiguration(
            runtime=runtime,
            schema=schema,
            text_layout_version=TEXT_LAYOUT_VERSION,
        )

        logger.info(
            "AI_CONFIG | phase=resolve_complete | config_id=%s | schema_version_id=%s | entities=%d | fields=%d | layout=%s",
            runtime.id,
            schema.version_id,
            len(entities),
            len(fields),
            TEXT_LAYOUT_VERSION,
        )

        return resolved