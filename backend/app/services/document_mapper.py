from app.db.models import DocumentModel
from app.domain.analysis import AnalysisStatus
from app.schemas.document import DocumentStatus, DocumentSummary


def derive_document_status(document: DocumentModel) -> DocumentStatus:
    analysis_statuses = {analysis.status for analysis in document.analyses}

    if AnalysisStatus.QUEUED.value in analysis_statuses or AnalysisStatus.PROCESSING.value in analysis_statuses:
        return DocumentStatus.PROCESSING

    if AnalysisStatus.READY.value in analysis_statuses:
        return DocumentStatus.READY

    if AnalysisStatus.ERROR.value in analysis_statuses:
        return DocumentStatus.ERROR

    return DocumentStatus(document.status)


def to_document_summary(document: DocumentModel) -> DocumentSummary:
    return DocumentSummary(
        id=document.id,
        name=document.original_name,
        pages=document.page_count if document.page_count is not None else 0,
        status=derive_document_status(document),
        uploaded_at=document.created_at.date(),
    )