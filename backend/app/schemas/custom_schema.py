"""Validate and serialize custom schema definitions, lifecycle operations, and version information.
"""

from datetime import datetime
from typing import Self
from uuid import UUID
from pydantic import Field, field_validator, model_validator

from app.schemas.base import ApiModel


class CustomEntityDefinitionRequest(ApiModel):
    """Validate the custom entity definition request payload exposed by the REST API."""

    label: str = Field(min_length=1, max_length=100, pattern=r"^[A-Z][A-Z0-9_]*$")
    description: str = Field(min_length=1, max_length=2000)

    @field_validator("label", "description", mode="before")
    @classmethod
    def strip_text(cls, value: object) -> object:
        """Trim extraneous whitespace from entity definition text fields."""

        if isinstance(value, str):
            return value.strip()

        return value


class CustomFieldDefinitionRequest(ApiModel):
    """Validate the custom field definition request payload exposed by the REST API."""

    field_key: str = Field(min_length=1, max_length=100, pattern=r"^[a-z][a-z0-9_]*$")
    label: str = Field(min_length=1, max_length=150)
    description: str = Field(min_length=1, max_length=2000)
    is_required: bool = False

    @field_validator("field_key", "label", "description", mode="before")
    @classmethod
    def strip_text(cls, value: object) -> object:
        """Trim extraneous whitespace from structured field definitions."""

        if isinstance(value, str):
            return value.strip()

        return value

    @field_validator("field_key")
    @classmethod
    def reject_reserved_field_key(cls, value: str) -> str:
        """Reject field keys reserved for internal extraction metadata."""

        if value == "confidence":
            raise ValueError("La chiave 'confidence' è riservata dal motore di estrazione.")

        return value


class CustomSchemaCreateRequest(ApiModel):
    """Validate the custom schema create request payload exposed by the REST API."""

    name: str = Field(min_length=1, max_length=120)
    domain: str = Field(min_length=1, max_length=120)
    entities: list[CustomEntityDefinitionRequest] = Field(default_factory=list, max_length=50)
    fields: list[CustomFieldDefinitionRequest] = Field(default_factory=list, max_length=50)

    @field_validator("name", "domain", mode="before")
    @classmethod
    def strip_text(cls, value: object) -> object:
        """Normalize whitespace in custom schema names and domain descriptions."""

        if isinstance(value, str):
            return value.strip()

        return value

    @model_validator(mode="after")
    def validate_definitions(self) -> Self:
        """Reject duplicate or otherwise invalid entity and field definitions."""

        if not self.entities and not self.fields:
            raise ValueError("Lo schema deve contenere almeno un'entità o un campo.")

        entity_labels = [entity.label for entity in self.entities]

        if len(entity_labels) != len(set(entity_labels)):
            raise ValueError("Le label delle entità devono essere univoche.")

        field_keys = [field.field_key for field in self.fields]

        if len(field_keys) != len(set(field_keys)):
            raise ValueError("Le chiavi dei campi devono essere univoche.")

        return self


class CustomSchemaUpdateRequest(CustomSchemaCreateRequest):
    """Validate the custom schema update request payload exposed by the REST API."""

    pass


class CustomEntityDefinitionResponse(ApiModel):
    """Serialize the custom entity definition data returned by the REST API."""

    id: UUID
    label: str
    description: str
    color: str
    sort_order: int


class CustomFieldDefinitionResponse(ApiModel):
    """Serialize the custom field definition data returned by the REST API."""

    id: UUID
    field_key: str
    label: str
    description: str
    data_type: str
    is_required: bool
    sort_order: int


class CustomSchemaResponse(ApiModel):
    """Serialize the custom schema data returned by the REST API."""

    schema_id: UUID
    schema_version_id: UUID
    name: str
    domain: str
    version: int
    created_at: datetime
    archived_at: datetime | None
    is_archived: bool
    entities: list[CustomEntityDefinitionResponse]
    fields: list[CustomFieldDefinitionResponse]


class CustomSchemaSummaryResponse(ApiModel):
    """Serialize the custom schema summary data returned by the REST API."""

    schema_id: UUID
    schema_version_id: UUID
    name: str
    domain: str
    version: int
    entity_count: int
    field_count: int
    created_at: datetime
    archived_at: datetime | None
    is_archived: bool


class CustomSchemaDuplicateRequest(ApiModel):
    """Validate the custom schema duplicate request payload exposed by the REST API."""

    name: str = Field(min_length=1, max_length=120)

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, value: object) -> object:
        """Normalize the requested name for a duplicated schema."""

        if isinstance(value, str):
            return value.strip()

        return value


class CustomSchemaArchiveResponse(ApiModel):
    """Serialize the custom schema archive data returned by the REST API."""

    schema_id: UUID
    archived_at: datetime
