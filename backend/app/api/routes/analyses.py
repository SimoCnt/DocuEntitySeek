from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from app.core.exceptions import AiConfigurationError, AnalysisExecutionError, AnalysisQuotaExceededError
from app.db.models import UserModel
from app.dependencies import AnalysisServiceDep, CurrentUserDep, AnalysisQueryServiceDep
from app.schemas.analysis import AnalysisPipelineSummaryResponse, AnalysisStartResponse, AnalysisSummaryResponse, AnalysisDetailResponse, AnalysisResultResponse, DocumentPageResponse, EntityOccurrenceResponse, ExtractedFieldResponse, FieldCandidateResponse, AnalysisStartRequest


router = APIRouter()


@router.post(
    "/documents/{document_id}/analyses",
    response_model=AnalysisStartResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_analysis(
    document_id: UUID,
    payload: AnalysisStartRequest,
    current_user: CurrentUserDep,
    service: AnalysisServiceDep,
) -> AnalysisStartResponse:
    try:
        result = service.run(
            document_id=document_id,
            owner_user_id=current_user.id,
            schema_version_id=payload.schema_version_id
        )

    except AnalysisQuotaExceededError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "ANALYSIS_QUOTA_EXCEEDED",
                "message": "Limite giornaliero di analisi raggiunto.",
                "dailyLimit": exc.daily_limit,
                "used": exc.used,
                "resetsAt": exc.resets_at.isoformat(),
            },
        ) from exc

    except AnalysisExecutionError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "ANALYSIS_FAILED",
                "message": "L'analisi non è stata completata.",
                "analysisId": str(exc.analysis_id),
            },
        ) from exc

    except AiConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "AI_CONFIGURATION_UNAVAILABLE",
                "message": "Il servizio di analisi non è temporaneamente disponibile.",
            },
        ) from exc

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "DOCUMENT_NOT_FOUND",
                "message": "Documento non trovato.",
            },
        ) from exc

    pipeline = result.pipeline

    return AnalysisStartResponse(
        analysis_id=result.analysis_id,
        status=result.status,
        pipeline=AnalysisPipelineSummaryResponse(
            page_count=pipeline.page_count,
            document_characters=pipeline.document_characters,
            entity_count=pipeline.entity_count,
            visible_entity_count=pipeline.visible_entity_count,
            hidden_entity_count=pipeline.hidden_entity_count,
            rejected_entity_count=pipeline.rejected_entity_count,
            field_count=pipeline.field_count,
            field_candidate_count=pipeline.field_candidate_count,
            extracted_field_count=pipeline.extracted_field_count,
            ambiguous_field_count=pipeline.ambiguous_field_count,
            not_found_field_count=pipeline.not_found_field_count,
            rejected_field_candidate_count=pipeline.rejected_field_candidate_count,
            elapsed_ms=pipeline.elapsed_ms,
        ),
    )


@router.get("/documents/{document_id}/analyses", response_model=list[AnalysisSummaryResponse])
def list_analyses(
    document_id: UUID,
    current_user: CurrentUserDep,
    service: AnalysisQueryServiceDep,
) -> list[AnalysisSummaryResponse]:
    analyses = service.list_for_document(
        document_id=document_id,
        owner_user_id=current_user.id,
    )

    return [
        AnalysisSummaryResponse(
            id=analysis.id,
            document_id=analysis.document_id,
            status=analysis.status,
            created_at=analysis.created_at,
            started_at=analysis.started_at,
            completed_at=analysis.completed_at,
            error_message=analysis.error_message,
            schema_version_id=analysis.schema_version_id,
            ai_runtime_config_id=analysis.ai_runtime_config_id,
        )
        for analysis in analyses
    ]


@router.get("/documents/{document_id}/analyses/{analysis_id}", response_model=AnalysisDetailResponse)
def get_analysis(
    document_id: UUID,
    analysis_id: UUID,
    current_user: CurrentUserDep,
    service: AnalysisQueryServiceDep,
) -> AnalysisDetailResponse:
    try:
        analysis, pages, entities, fields, candidates_by_field = service.get_detail(
            analysis_id=analysis_id,
            document_id=document_id,
            owner_user_id=current_user.id,
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "ANALYSIS_NOT_FOUND",
                "message": "Analisi non trovata.",
            },
        ) from exc

    result = None

    if analysis.status == "READY":
        result = AnalysisResultResponse(
            pages=[
                DocumentPageResponse(
                    page_number=page.page_number,
                    text=page.extracted_text,
                    global_start=page.global_start,
                    global_end=page.global_end,
                )
                for page in pages
            ],
            entities=[
                EntityOccurrenceResponse(
                    id=entity.id,
                    label=entity.label,
                    text=entity.text,
                    confidence=float(entity.confidence),
                    global_start=entity.global_start,
                    global_end=entity.global_end,
                    page=entity.page,
                    page_start=entity.page_start,
                    page_end=entity.page_end,
                    is_visible=entity.is_visible,
                )
                for entity in entities
            ],
            fields=[
                ExtractedFieldResponse(
                    id=field.id,
                    field_key=field.field_key,
                    status=field.status,
                    value=field.value_text,
                    confidence=float(field.confidence) if field.confidence is not None else None,
                    page=field.page,
                    global_start=field.global_start,
                    global_end=field.global_end,
                    candidates=[
                        FieldCandidateResponse(
                            id=candidate.id,
                            value=candidate.value_text,
                            confidence=float(candidate.confidence),
                            page=candidate.page,
                            global_start=candidate.global_start,
                            global_end=candidate.global_end,
                            rank=candidate.candidate_rank,
                        )
                        for candidate in candidates_by_field[field.id]
                    ],
                )
                for field in fields
            ],
        )

    return AnalysisDetailResponse(
        id=analysis.id,
        document_id=analysis.document_id,
        status=analysis.status,
        created_at=analysis.created_at,
        started_at=analysis.started_at,
        completed_at=analysis.completed_at,
        error_message=analysis.error_message,
        schema_version_id=analysis.schema_version_id,
        ai_runtime_config_id=analysis.ai_runtime_config_id,
        result=result,
    )