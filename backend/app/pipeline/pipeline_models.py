"""Describe the aggregate metrics returned after a complete AI pipeline run."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AiPipelineExecutionResult:
    """Pipeline metrics and outcome returned to the application service."""

    runtime_config_id: UUID
    schema_version_id: UUID
    page_count: int
    document_characters: int
    entity_count: int
    visible_entity_count: int
    hidden_entity_count: int
    rejected_entity_count: int
    field_count: int
    field_candidate_count: int
    extracted_field_count: int
    ambiguous_field_count: int
    not_found_field_count: int
    rejected_field_candidate_count: int
    elapsed_ms: float
