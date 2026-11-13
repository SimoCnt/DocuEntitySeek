from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExtractedPdfPage:
    page_number: int
    text: str

    @property
    def char_count(self) -> int:
        return len(self.text)


@dataclass(frozen=True, slots=True)
class PdfExtractionResult:
    pages: tuple[ExtractedPdfPage, ...]

    @property
    def page_count(self) -> int:
        return len(self.pages)

    @property
    def total_characters(self) -> int:
        return sum(page.char_count for page in self.pages)

    @property
    def empty_page_count(self) -> int:
        return sum(not page.text.strip() for page in self.pages)