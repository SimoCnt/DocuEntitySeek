"""Expose analysis execution, history, results, and original-PDF highlight geometry endpoints."""

from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.core.exceptions import (
    AiConfigurationError,
    AnalysisExecutionError,
    AnalysisQuotaExceededError,
    CustomSchemasNotAvailableError,
    ExtractionSchemaNotFoundError,
)
from app.dependencies import AnalysisQueryServiceDep, AnalysisServiceDep, CurrentUserDep, DocumentStorageDep, DbSessionDep
from app.schemas.analysis import (
    AnalysisDetailResponse,
    PdfPageGeometryResponse,
    AnalysisEntityDefinitionResponse,
    AnalysisFieldDefinitionResponse,
    AnalysisPipelineSummaryResponse,
    AnalysisResultResponse,
    AnalysisSchemaResponse,
    AnalysisStartRequest,
    AnalysisStartResponse,
    AnalysisSummaryResponse,
    DocumentPageResponse,
    EntityOccurrenceResponse,
    ExtractedFieldResponse,
    FieldCandidateResponse,
)

from app.core.config import get_settings
from app.core.exceptions import DocumentStorageError
from app.repositories.document_repository import DocumentRepository
from app.services.pdf_geometry_service import PdfGeometryService, TextRegionRequest


router = APIRouter()


@router.post(
    "/documents/{document_id}/analyses",
    response_model=AnalysisStartResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_analysis(
    document_id: UUID,
    current_user: CurrentUserDep,
    service: AnalysisServiceDep,
    payload: AnalysisStartRequest | None = None,
) -> AnalysisStartResponse:
    """Authorize a schema and execute a document analysis in the HTTP request.

    The current implementation is synchronous despite initially recording
    the analysis in QUEUED state. Quota, authorization, AI, and execution
    failures are translated to stable HTTP error codes.
    """

    try:
        result = service.run(
            document_id=document_id,
            owner_user_id=current_user.id,
            schema_version_id=payload.schema_version_id if payload is not None else None,
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

    except ExtractionSchemaNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "EXTRACTION_SCHEMA_NOT_FOUND",
                "message": "Schema di estrazione non trovato.",
            },
        ) from exc

    except CustomSchemasNotAvailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "CUSTOM_SCHEMAS_NOT_AVAILABLE",
                "message": "Gli schema personalizzati richiedono un piano che li supporti.",
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


@router.get(
    "/documents/{document_id}/analyses",
    response_model=list[AnalysisSummaryResponse],
)
def list_analyses(
    document_id: UUID,
    current_user: CurrentUserDep,
    service: AnalysisQueryServiceDep,
) -> list[AnalysisSummaryResponse]:
    """Return owner-authorized analysis history with schema names and versions."""

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
            schema_name=analysis.schema_version.schema.name,
            schema_version=analysis.schema_version.version,
            ai_runtime_config_id=analysis.ai_runtime_config_id,
        )
        for analysis in analyses
    ]


@router.get(
    "/documents/{document_id}/analyses/{analysis_id}",
    response_model=AnalysisDetailResponse,
)
def get_analysis(
    document_id: UUID,
    analysis_id: UUID,
    current_user: CurrentUserDep,
    service: AnalysisQueryServiceDep,
) -> AnalysisDetailResponse:
    """Return analysis metadata and, for READY analyses, persisted extraction results."""

    try:
        (
            analysis,
            schema_version,
            pages,
            entities,
            fields,
            candidates_by_field,
        ) = service.get_detail(
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
        if schema_version is None:
            raise RuntimeError(
                "Schema version associata all'Analysis non trovata."
            )

        schema = AnalysisSchemaResponse(
            schema_id=schema_version.schema.id,
            schema_version_id=schema_version.id,
            name=schema_version.schema.name,
            domain=schema_version.schema.domain,
            version=schema_version.version,
            entity_definitions=[
                AnalysisEntityDefinitionResponse(
                    label=definition.label,
                    description=definition.description,
                    color=definition.color,
                    sort_order=definition.sort_order,
                )
                for definition in sorted(
                    schema_version.entity_definitions,
                    key=lambda item: item.sort_order,
                )
            ],
            field_definitions=[
                AnalysisFieldDefinitionResponse(
                    field_key=definition.field_key,
                    label=definition.label,
                    description=definition.description,
                    data_type=definition.data_type,
                    is_required=definition.is_required,
                    sort_order=definition.sort_order,
                )
                for definition in sorted(
                    schema_version.field_definitions,
                    key=lambda item: item.sort_order,
                )
            ],
        )

        result = AnalysisResultResponse(
            schema=schema,
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


@router.get(
    "/documents/{document_id}/analyses/{analysis_id}/geometry",
    response_model=PdfPageGeometryResponse,
)
def get_pdf_page_geometry(
    document_id: UUID,
    analysis_id: UUID,
    page_number: Annotated[int, Query(ge=1)],
    current_user: CurrentUserDep,
    service: AnalysisQueryServiceDep,
    storage: DocumentStorageDep,
    session: DbSessionDep,
) -> PdfPageGeometryResponse:
    """Map visible AI spans to verified rectangles on an original PDF page.

    The service compares persisted extracted text with actual PDF text
    before returning geometry; unaligned results are not highlighted.
    """

    try:
        analysis, _, pages, entities, fields, _ = service.get_detail(
            analysis_id=analysis_id, document_id=document_id, owner_user_id=current_user.id
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Analisi non trovata.") from exc

    if analysis.status != "READY":
        raise HTTPException(status_code=409, detail="Analisi non ancora completata.")

    page = next((item for item in pages if item.page_number == page_number), None)
    if page is None:
        raise HTTPException(status_code=404, detail="Pagina non trovata.")

    document = DocumentRepository(session).get_by_id_and_owner(document_id, current_user.id)
    if document is None or not document.storage_key:
        raise HTTPException(status_code=404, detail="PDF originale non disponibile.")

    requests = []
    for entity in entities:
        if entity.page == page_number and entity.is_visible and 0 <= entity.page_start < entity.page_end <= len(page.extracted_text):
            if page.extracted_text[entity.page_start:entity.page_end] == entity.text:
                requests.append(TextRegionRequest("entity", str(entity.id), entity.label, entity.page_start, entity.page_end))
    for field in fields:
        if field.page == page_number and field.value_text and field.global_start is not None and field.global_end is not None:
            start = field.global_start - page.global_start
            end = field.global_end - page.global_start
            if 0 <= start < end <= len(page.extracted_text) and page.extracted_text[start:end] == field.value_text:
                requests.append(TextRegionRequest("field", str(field.id), field.field_key, start, end))

    try:
        with storage.materialize(document.storage_key) as pdf_path:
            result = PdfGeometryService(sort_text=get_settings().pdf_text_sort).map_page(
                pdf_path=pdf_path, page_number=page_number,
                expected_text=page.extracted_text, regions=requests,
            )
    except (DocumentStorageError, FileNotFoundError) as exc:
        raise HTTPException(status_code=404, detail="PDF originale non disponibile.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="PDF o pagina non validi.") from exc

    return PdfPageGeometryResponse.model_validate(result)

