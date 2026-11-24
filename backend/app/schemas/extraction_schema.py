"""Describe extraction schemas available to the currently authenticated user."""

from uuid import UUID

from app.schemas.base import ApiModel


class AvailableExtractionSchemaResponse(ApiModel):
    """Serialize the available extraction schema data returned by the REST API."""

    schema_id: UUID
    schema_version_id: UUID
    name: str
    domain: str
    version: int
    is_builtin: bool
