from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class RuntimeAiConfig:
    id: UUID
    name: str
    version: int
    engine: str
    model_id: str
    model_revision: str | None
    chunk_size: int
    chunk_overlap: int
    batch_size: int
    num_workers: int
    overlap_policy: str
    entity_threshold: float
    field_threshold: float


@dataclass(frozen=True, slots=True)
class EntityExtractionDefinition:
    id: UUID
    label: str
    description: str


@dataclass(frozen=True, slots=True)
class FieldExtractionDefinition:
    id: UUID
    field_key: str
    label: str
    description: str
    data_type: str
    is_required: bool


@dataclass(frozen=True, slots=True)
class ResolvedExtractionSchema:
    schema_id: UUID
    schema_name: str
    schema_domain: str
    version_id: UUID
    version: int
    entities: tuple[EntityExtractionDefinition, ...]
    fields: tuple[FieldExtractionDefinition, ...]


@dataclass(frozen=True, slots=True)
class ResolvedAiConfiguration:
    runtime: RuntimeAiConfig
    schema: ResolvedExtractionSchema
    text_layout_version: str

    def to_snapshot(self) -> dict[str, object]:
        return {
            "runtimeConfig": {
                "id": str(self.runtime.id),
                "name": self.runtime.name,
                "version": self.runtime.version,
                "engine": self.runtime.engine,
                "modelId": self.runtime.model_id,
                "modelRevision": self.runtime.model_revision,
                "chunkSize": self.runtime.chunk_size,
                "chunkOverlap": self.runtime.chunk_overlap,
                "entityThreshold": self.runtime.entity_threshold,
                "fieldThreshold": self.runtime.field_threshold,
                "batchSize": self.runtime.batch_size,
                "numWorkers": self.runtime.num_workers,
                "overlapPolicy": self.runtime.overlap_policy,
            },
            "schema": {
                "schemaId": str(self.schema.schema_id),
                "structureKey": self.schema.structure_key,
                "name": self.schema.schema_name,
                "domain": self.schema.schema_domain,
                "versionId": str(self.schema.version_id),
                "version": self.schema.version,
            },
            "textLayoutVersion": self.text_layout_version,
        }


@dataclass(frozen=True, slots=True)
class ResolvedExtractionSchema:
    schema_id: UUID
    schema_name: str
    schema_domain: str
    structure_key: str
    version_id: UUID
    version: int
    entities: tuple[EntityExtractionDefinition, ...]
    fields: tuple[FieldExtractionDefinition, ...]