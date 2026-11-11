
from collections import defaultdict

from app.db.models import AnalysisModel, DocumentModel, EntityOccurrenceModel
from app.schemas.document import DocumentCategory, DocumentStatus, DocumentSummary
from app.schemas.analysis import DocumentAnalysis, DocumentPage, EntityDefinition, EntitySegment, ExtractedField, ExtractedFieldStatus, TextOnlySegment


def to_document_summary(document: DocumentModel) -> DocumentSummary:
    return DocumentSummary(
        id=document.id,
        name=document.original_name,
        category=DocumentCategory(document.category),
        pages=document.page_count if document.page_count is not None else 0,
        status=DocumentStatus(document.status),
        uploaded_at=document.created_at.date(),
    )


def build_document_analysis(document: DocumentModel, analysis: AnalysisModel) -> DocumentAnalysis:
    definitions = sorted(analysis.schema_version.entity_definitions, key=lambda item: item.sort_order)
    entity_definitions = [EntityDefinition(label=item.label, color=item.color) for item in definitions]
    occurrences_by_page: dict[int, list[EntityOccurrenceModel]] = defaultdict(list)

    for occurrence in analysis.entity_occurrences:
        if occurrence.is_visible:
            occurrences_by_page[occurrence.page].append(occurrence)

    pages = [_build_page(page=page, occurrences=occurrences_by_page[page.page_number]) for page in document.pages]
    field_labels = {definition.field_key: definition.label for definition in analysis.schema_version.field_definitions}

    extracted_fields = [
        ExtractedField(
            id=field.id,
            label=field_labels.get(field.field_key, field.field_key),
            value=field.value_text,
            page=field.page,
            confidence=float(field.confidence) if field.confidence is not None else None,
            status=ExtractedFieldStatus(field.status),
        )
        for field in sorted(analysis.extracted_fields, key=lambda item: item.field_key)
    ]

    return DocumentAnalysis(
        entity_definitions=entity_definitions,
        pages=pages,
        extracted_fields=extracted_fields,
    )


def _build_page(*, page, occurrences: list[EntityOccurrenceModel]) -> DocumentPage:
    text = page.extracted_text
    sorted_occurrences = sorted(occurrences, key=lambda item: (item.page_start, item.page_end))
    segments = []
    cursor = 0

    for occurrence in sorted_occurrences:
        start = max(0, min(occurrence.page_start, len(text)))
        end = max(start, min(occurrence.page_end, len(text)))

        # Ignora le entità sovrapposte a quelle già visualizzate nel viewer flat.
        if start < cursor or end <= start:
            continue

        if start > cursor:
            segments.append(TextOnlySegment(type="text", text=text[cursor:start]))

        entity_text = text[start:end]

        if not entity_text:
            entity_text = occurrence.text

        segments.append(
            EntitySegment(type="entity", id=occurrence.id, text=entity_text, label=occurrence.label)
        )
        cursor = end

    if cursor < len(text):
        segments.append(TextOnlySegment(type="text", text=text[cursor:]))

    return DocumentPage(page_number=page.page_number, segments=segments)
