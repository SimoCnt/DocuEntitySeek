"""Describe the analysis execution result returned to the API."""

from dataclasses import dataclass
from uuid import UUID

from app.pipeline.pipeline_models import AiPipelineExecutionResult


@dataclass(frozen=True, slots=True)
class AnalysisExecutionResult:
    """Application result containing analysis identity, state, and pipeline statistics."""

    analysis_id: UUID
    status: str
    pipeline: AiPipelineExecutionResult
