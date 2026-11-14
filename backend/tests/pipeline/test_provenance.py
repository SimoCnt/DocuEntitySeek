from uuid import uuid4

import pytest

from app.pipeline.models import ExtractedPdfPage, PdfExtractionResult
from app.pipeline.provenance import DocumentProvenanceBuilder, PAGE_SEPARATOR, TEXT_LAYOUT_VERSION


@pytest.mark.unit
def test_build_global_text_and_offsets() -> None:
    extraction = PdfExtractionResult(
        pages=(
            ExtractedPdfPage(page_number=1, text="ABC"),
            ExtractedPdfPage(page_number=2, text="DEFG"),
            ExtractedPdfPage(page_number=3, text="HI"),
        )
    )

    builder = DocumentProvenanceBuilder()
    result = builder.build(document_id=uuid4(), extraction=extraction)
    expected_text = "ABC" + PAGE_SEPARATOR + "DEFG" + PAGE_SEPARATOR + "HI"

    assert result.text == expected_text
    assert result.layout_version == TEXT_LAYOUT_VERSION
    assert result.pages[0].global_start == 0
    assert result.pages[0].global_end == 3
    assert result.pages[1].global_start == 3 + len(PAGE_SEPARATOR)
    assert result.text[result.pages[1].global_start:result.pages[1].global_end] == "DEFG"


@pytest.mark.unit
def test_every_page_can_be_reconstructed_from_global_text() -> None:
    extraction = PdfExtractionResult(
        pages=(
            ExtractedPdfPage(page_number=1, text="Prima pagina\n"),
            ExtractedPdfPage(page_number=2, text="Seconda pagina\n"),
        )
    )

    result = DocumentProvenanceBuilder().build(document_id=uuid4(), extraction=extraction)

    for page in result.pages:
        assert result.text[page.global_start:page.global_end] == page.text


@pytest.mark.unit
def test_empty_page_has_zero_length_span() -> None:
    extraction = PdfExtractionResult(
        pages=(
            ExtractedPdfPage(page_number=1, text="ABC"),
            ExtractedPdfPage(page_number=2, text=""),
            ExtractedPdfPage(page_number=3, text="DEF"),
        )
    )

    result = DocumentProvenanceBuilder().build(document_id=uuid4(), extraction=extraction)
    empty_page = result.pages[1]

    assert empty_page.global_start == empty_page.global_end
    assert result.text[empty_page.global_start:empty_page.global_end] == ""