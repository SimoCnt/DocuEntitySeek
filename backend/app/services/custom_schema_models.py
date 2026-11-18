from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CustomEntityDefinitionInput:
    label: str
    description: str


@dataclass(frozen=True, slots=True)
class CustomFieldDefinitionInput:
    field_key: str
    label: str
    description: str
    is_required: bool


@dataclass(frozen=True, slots=True)
class CustomSchemaCreateCommand:
    name: str
    domain: str
    entities: tuple[CustomEntityDefinitionInput, ...]
    fields: tuple[CustomFieldDefinitionInput, ...]


@dataclass(frozen=True, slots=True)
class CustomEntityDefinitionResult:
    id: UUID
    label: str
    description: str
    color: str
    sort_order: int


@dataclass(frozen=True, slots=True)
class CustomFieldDefinitionResult:
    id: UUID
    field_key: str
    label: str
    description: str
    data_type: str
    is_required: bool
    sort_order: int


@dataclass(frozen=True, slots=True)
class CustomSchemaResult:
    schema_id: UUID
    schema_version_id: UUID
    name: str
    domain: str
    version: int
    created_at: datetime
    archived_at: datetime | None
    entities: tuple[CustomEntityDefinitionResult, ...]
    fields: tuple[CustomFieldDefinitionResult, ...]


@dataclass(frozen=True, slots=True)
class CustomSchemaSummary:
    schema_id: UUID
    schema_version_id: UUID
    name: str
    domain: str
    version: int
    entity_count: int
    field_count: int
    created_at: datetime
    archived_at: datetime | None