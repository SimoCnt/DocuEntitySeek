from uuid import uuid4
import pytest

from app.pipeline.field_models import StructuredExtractionResult, StructuredFieldCandidate
from app.pipeline.models import ExtractedPdfPage, PdfExtractionResult
from app.pipeline.ner_models import NerCandidate, ViewerNerDecision, ViewerNerSelectionResult
from app.pipeline.page_mapping_models import SpanMappingFailureReason
from app.pipeline.page_span_mapper import PageSpanMapper
from app.pipeline.provenance import DocumentProvenanceBuilder


def make_document():
    extraction = PdfExtractionResult(
        pages=(
            ExtractedPdfPage(page_number=1, text="ABC"),
            ExtractedPdfPage(page_number=2, text="Comune di Palermo"),
            ExtractedPdfPage(page_number=3, text="DEF"),
        )
    )

    return DocumentProvenanceBuilder().build(document_id=uuid4(), extraction=extraction)


@pytest.mark.unit
def test_ner_global_span_is_mapped_to_page_coordinates() -> None:
    document = make_document()

    text = "Comune di Palermo"
    start = document.text.index(text)
    end = start + len(text)

    selection = ViewerNerSelectionResult(
        decisions=(
            ViewerNerDecision(
                candidate=NerCandidate(label="ENTE_TEST", text=text, start=start, end=end, confidence=0.95),
                is_visible=True,
            ),
        )
    )

    result = PageSpanMapper().map_ner(
        document_id=uuid4(),
        document=document,
        selection=selection,
    )

    assert result.mapped_count == 1
    assert result.rejected_count == 0

    mapped = result.mapped[0]

    assert mapped.page_number == 2
    assert mapped.page_start == 0
    assert mapped.page_end == len(text)
    assert mapped.is_visible is True

    page = document.pages[1]

    assert (page.text[mapped.page_start:mapped.page_end] == text)


@pytest.mark.unit
def test_hidden_ner_remains_hidden_after_page_mapping() -> None:
    document = make_document()

    text = "Comune di Palermo"
    start = document.text.index(text)

    selection = ViewerNerSelectionResult(
        decisions=(
            ViewerNerDecision(
                candidate=NerCandidate(
                    label="ENTE_TEST",
                    text=text,
                    start=start,
                    end=start + len(text),
                    confidence=0.80,
                ),
                is_visible=False,
            ),
        )
    )

    result = PageSpanMapper().map_ner(
        document_id=uuid4(),
        document=document,
        selection=selection,
    )

    assert result.mapped_count == 1
    assert result.mapped[0].is_visible is False


@pytest.mark.unit
def test_span_starting_in_page_separator_is_rejected() -> None:
    document = make_document()
    first_page = document.pages[0]

    start = first_page.global_end
    end = start + 1

    selection = ViewerNerSelectionResult(
        decisions=(
            ViewerNerDecision(
                candidate=NerCandidate(
                    label="TEST",
                    text=document.text[start:end],
                    start=start,
                    end=end,
                    confidence=0.90,
                ),
                is_visible=True,
            ),
        )
    )

    result = PageSpanMapper().map_ner(
        document_id=uuid4(),
        document=document,
        selection=selection,
    )

    assert result.mapped_count == 0
    assert result.rejected_count == 1
    assert result.rejected[0].reason == SpanMappingFailureReason.START_IN_PAGE_SEPARATOR


@pytest.mark.unit
def test_span_ending_in_page_separator_is_rejected() -> None:
    document = make_document()
    first_page = document.pages[0]

    start = first_page.global_end - 1
    end = first_page.global_end + 1

    selection = ViewerNerSelectionResult(
        decisions=(
            ViewerNerDecision(
                candidate=NerCandidate(
                    label="TEST",
                    text=document.text[start:end],
                    start=start,
                    end=end,
                    confidence=0.90,
                ),
                is_visible=True,
            ),
        )
    )

    result = PageSpanMapper().map_ner(
        document_id=uuid4(),
        document=document,
        selection=selection,
    )

    assert result.rejected_count == 1
    assert result.rejected[0].reason == SpanMappingFailureReason.END_IN_PAGE_SEPARATOR


@pytest.mark.unit
def test_cross_page_span_is_rejected_explicitly() -> None:
    document = make_document()

    page_1 = document.pages[0]
    page_2 = document.pages[1]

    start = page_1.global_end - 1
    end = page_2.global_start + 1

    selection = ViewerNerSelectionResult(
        decisions=(
            ViewerNerDecision(
                candidate=NerCandidate(
                    label="TEST",
                    text=document.text[start:end],
                    start=start,
                    end=end,
                    confidence=0.90,
                ),
                is_visible=True,
            ),
        )
    )

    result = PageSpanMapper().map_ner(
        document_id=uuid4(),
        document=document,
        selection=selection,
    )

    assert result.mapped_count == 0
    assert result.rejected_count == 1
    assert result.rejected[0].reason == SpanMappingFailureReason.CROSS_PAGE


@pytest.mark.unit
def test_field_candidate_is_mapped_to_page_coordinates() -> None:
    document = make_document()

    value = "Comune di Palermo"
    start = document.text.index(value)

    extraction = StructuredExtractionResult(
        candidates=(
            StructuredFieldCandidate(
                field_key="campo_test",
                value=value,
                start=start,
                end=start + len(value),
                confidence=0.94,
                record_index=0,
                item_index=0,
            ),
        ),
        expected_field_keys=("campo_test",),
        record_count=1,
    )

    result = PageSpanMapper().map_fields(
        document_id=uuid4(),
        document=document,
        result=extraction,
    )

    assert result.mapped_count == 1
    assert result.rejected_count == 0

    mapped = result.mapped[0]

    assert mapped.page_number == 2
    assert mapped.page_start == 0
    assert mapped.page_end == len(value)


@pytest.mark.unit
def test_local_page_offsets_are_relative_to_page_start() -> None:
    document = make_document()

    value = "Palermo"
    start = document.text.index(value)

    extraction = StructuredExtractionResult(
        candidates=(
            StructuredFieldCandidate(
                field_key="campo_test",
                value=value,
                start=start,
                end=start + len(value),
                confidence=0.90,
                record_index=0,
                item_index=0,
            ),
        ),
        expected_field_keys=("campo_test",),
        record_count=1,
    )

    result = PageSpanMapper().map_fields(
        document_id=uuid4(),
        document=document,
        result=extraction,
    )

    mapped = result.mapped[0]

    assert mapped.page_number == 2
    assert mapped.page_start == len("Comune di ")
    assert mapped.page_end == len("Comune di Palermo")