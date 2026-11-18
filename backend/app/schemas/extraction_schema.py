from uuid import UUID

from app.schemas.base import ApiModel


class AvailableExtractionSchemaResponse(ApiModel):
    schema_id: UUID
    schema_version_id: UUID
    name: str
    domain: str
    version: int
    is_builtin: bool