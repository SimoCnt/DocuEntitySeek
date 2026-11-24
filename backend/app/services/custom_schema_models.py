"""Define commands and result objects for custom extraction-schema workflows."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CustomEntityDefinitionInput:
    """Entity definition supplied to a custom-schema command."""

    label: str
    description: str


@dataclass(frozen=True, slots=True)
class CustomFieldDefinitionInput:
    """Field definition supplied to a custom-schema command."""

    field_key: str
    label: str
    description: str
    is_required: bool


@dataclass(frozen=True, slots=True)
class CustomSchemaCreateCommand:
    """Normalized command describing a new or updated custom schema."""

    name: str
    domain: str
    entities: tuple[CustomEntityDefinitionInput, ...]
    fields: tuple[CustomFieldDefinitionInput, ...]


@dataclass(frozen=True, slots=True)
class CustomEntityDefinitionResult:
    """Entity definition returned by the custom-schema service."""

    id: UUID
    label: str
    description: str
    color: str
    sort_order: int


@dataclass(frozen=True, slots=True)
class CustomFieldDefinitionResult:
    """Field definition returned by the custom-schema service."""

    id: UUID
    field_key: str
    label: str
    description: str
    data_type: str
    is_required: bool
    sort_order: int


@dataclass(frozen=True, slots=True)
class CustomSchemaResult:
    """Fully populated custom schema version returned by the service."""

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
    """Condensed custom-schema metadata for listings."""

    schema_id: UUID
    schema_version_id: UUID
    name: str
    domain: str
    version: int
    entity_count: int
    field_count: int
    created_at: datetime
    archived_at: datetime | None
