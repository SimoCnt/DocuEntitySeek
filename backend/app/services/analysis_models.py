from dataclasses import dataclass
from uuid import UUID

from app.pipeline.pipeline_models import AiPipelineExecutionResult


@dataclass(frozen=True, slots=True)
class AnalysisExecutionResult:
    analysis_id: UUID
    status: str
    pipeline: AiPipelineExecutionResult