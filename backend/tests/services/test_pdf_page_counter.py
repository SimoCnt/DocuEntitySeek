"""Test del conteggio pagine: nessuna dipendenza da S3 o PostgreSQL."""
from io import BytesIO
import pymupdf
import pytest

from app.core.exceptions import InvalidDocumentFileError
from app.services.pdf_page_counter import count_pdf_pages


def make_pdf(page_count: int) -> bytes:
    with pymupdf.open() as document:
        for _ in range(page_count):
            document.new_page()
        return document.tobytes()


def test_counts_pages_before_ai_analysis():
    source = BytesIO(make_pdf(3))
    assert count_pdf_pages(source) == 3
    assert source.tell() == 0
    assert not source.closed


def test_pdf_without_text_is_still_counted():
    assert count_pdf_pages(BytesIO(make_pdf(2))) == 2


def test_invalid_pdf_is_rejected_and_stream_reset():
    source = BytesIO(b"%PDF-1.7\nnot a valid pdf")
    with pytest.raises(InvalidDocumentFileError):
        count_pdf_pages(source)
    assert source.tell() == 0
