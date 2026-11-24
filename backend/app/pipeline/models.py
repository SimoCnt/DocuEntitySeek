"""Represent extracted PDF pages and the normalized text/provenance used for AI inference."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExtractedPdfPage:
    """Per-page PDF text before global offset assignment."""

    page_number: int
    text: str

    @property
    def char_count(self) -> int:
        """Return the extracted character count for this PDF page."""

        return len(self.text)


@dataclass(frozen=True, slots=True)
class PdfExtractionResult:
    """Collection of extracted PDF pages and extraction diagnostics."""

    pages: tuple[ExtractedPdfPage, ...]

    @property
    def page_count(self) -> int:
        """Return the number of pages represented by the extraction."""

        return len(self.pages)

    @property
    def total_characters(self) -> int:
        """Return the sum of extracted text characters across PDF pages."""

        return sum(page.char_count for page in self.pages)

    @property
    def empty_page_count(self) -> int:
        """Return the number of pages with no extractable text."""

        return sum(not page.text.strip() for page in self.pages)
    

@dataclass(frozen=True, slots=True)
class PreparedDocumentPage:
    """Page text with global and page-local provenance boundaries."""

    page_number: int
    text: str
    global_start: int
    global_end: int

    @property
    def char_count(self) -> int:
        """Return the number of characters in the prepared page text."""

        return len(self.text)


@dataclass(frozen=True, slots=True)
class PreparedDocumentText:
    """Global text assembled from pages with a stable offset layout."""

    text: str
    pages: tuple[PreparedDocumentPage, ...]
    layout_version: str

    @property
    def page_count(self) -> int:
        """Return the number of pages in the prepared document."""

        return len(self.pages)

    @property
    def total_characters(self) -> int:
        """Return the character count of the joined document text."""

        return len(self.text)
