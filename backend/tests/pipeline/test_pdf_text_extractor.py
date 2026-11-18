from uuid import uuid4

import pymupdf
import pytest

from app.core.exceptions import PdfTextExtractionError
from app.pipeline.pdf_text_extractor import PdfTextExtractor


@pytest.fixture
def text_pdf(tmp_path):
    pdf_path = tmp_path / "document.pdf"
    document = pymupdf.open()

    page_1 = document.new_page()
    page_1.insert_text((72, 72), "Prima pagina del disciplinare.")

    page_2 = document.new_page()
    page_2.insert_text((72, 72), "Seconda pagina del disciplinare.")

    document.save(pdf_path)
    document.close()

    return pdf_path


@pytest.mark.unit
def test_extract_text_page_by_page(text_pdf) -> None:
    extractor = PdfTextExtractor()
    result = extractor.extract(document_id=uuid4(), pdf_path=text_pdf)

    assert result.page_count == 2
    assert result.empty_page_count == 0
    assert "Prima pagina" in result.pages[0].text
    assert "Seconda pagina" in result.pages[1].text
    assert result.pages[0].page_number == 1
    assert result.pages[1].page_number == 2
    assert result.total_characters > 0


@pytest.mark.unit
def test_missing_pdf_raises_error(tmp_path) -> None:
    extractor = PdfTextExtractor()

    with pytest.raises(PdfTextExtractionError):
        extractor.extract(document_id=uuid4(), pdf_path=tmp_path / "missing.pdf")


@pytest.mark.unit
def test_image_only_or_empty_pdf_is_rejected(tmp_path) -> None:
    pdf_path = tmp_path / "empty.pdf"

    document = pymupdf.open()
    document.new_page()
    document.save(pdf_path)
    document.close()

    extractor = PdfTextExtractor()

    with pytest.raises(PdfTextExtractionError, match="non contiene testo estraibile"):
        extractor.extract(document_id=uuid4(), pdf_path=pdf_path)