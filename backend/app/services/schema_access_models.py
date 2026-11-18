from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AvailableExtractionSchema:
    schema_id: UUID
    schema_version_id: UUID
    name: str
    domain: str
    version: int
    is_builtin: bool