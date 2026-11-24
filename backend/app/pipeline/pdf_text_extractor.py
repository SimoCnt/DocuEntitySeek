"""Extract per-page PDF text using PyMuPDF, tracking empty pages and extraction failures."""

from pathlib import Path
from time import perf_counter
from uuid import UUID
import pymupdf

from app.core.exceptions import PdfTextExtractionError
from app.core.logging import get_logger
from app.pipeline.models import ExtractedPdfPage, PdfExtractionResult


logger = get_logger("pipeline.pdf")


class PdfTextExtractor:
    """Extract PDF page text with PyMuPDF and preserve page numbering."""

    def __init__(self, *, sort_text: bool = False) -> None:
        self.sort_text = sort_text


    def extract(
            self, 
            *, 
            document_id: UUID, 
            pdf_path: Path
            ) -> PdfExtractionResult:
        """Read text from every PDF page, preserving page order and extraction diagnostics."""

        started_at = perf_counter()
        resolved_path = pdf_path.resolve()

        logger.info(
            "PDF_EXTRACTION | phase=start | document_id=%s | path=%s",
            document_id,
            resolved_path,
        )

        if not resolved_path.is_file():
            logger.error(
                "PDF_EXTRACTION | phase=file_missing | document_id=%s | path=%s",
                document_id,
                resolved_path,
            )

            raise PdfTextExtractionError("Il PDF associato al documento non esiste nello storage.")

        try:
            with pymupdf.open(resolved_path) as document:
                if not document.is_pdf:
                    logger.error("PDF_EXTRACTION | phase=invalid_format | document_id=%s", document_id)

                    raise PdfTextExtractionError("Il documento salvato non è un PDF valido.")

                if document.needs_pass:
                    logger.warning("PDF_EXTRACTION | phase=password_required | document_id=%s", document_id)

                    raise PdfTextExtractionError("Il PDF è protetto da password.")

                logger.info(
                    "PDF_EXTRACTION | phase=document_opened | document_id=%s | pages=%d | repaired=%s | sort=%s",
                    document_id,
                    document.page_count,
                    document.is_repaired,
                    self.sort_text,
                )

                if document.is_repaired:
                    logger.warning("PDF_EXTRACTION | phase=document_repaired | document_id=%s", document_id)

                pages: list[ExtractedPdfPage] = []

                for page_index, page in enumerate(document):
                    page_number = page_index + 1

                    logger.debug(
                        "PDF_EXTRACTION | phase=page_start | document_id=%s | page=%d",
                        document_id,
                        page_number,
                    )

                    text = page.get_text("text", sort=self.sort_text)
                    extracted_page = ExtractedPdfPage(page_number=page_number, text=text)
                    pages.append(extracted_page)

                    if not text.strip():
                        logger.warning(
                            "PDF_EXTRACTION | phase=page_empty | document_id=%s | page=%d",
                            document_id,
                            page_number,
                        )
                    else:
                        logger.debug(
                            "PDF_EXTRACTION | phase=page_complete | document_id=%s | page=%d | chars=%d",
                            document_id,
                            page_number,
                            extracted_page.char_count,
                        )

                result = PdfExtractionResult(pages=tuple(pages))

                if result.page_count == 0:
                    raise PdfTextExtractionError("Il PDF non contiene pagine.")

                if result.total_characters == 0:
                    logger.warning(
                        "PDF_EXTRACTION | phase=no_text_detected | document_id=%s | pages=%d",
                        document_id,
                        result.page_count,
                    )

                    raise PdfTextExtractionError(
                        "Il PDF non contiene testo estraibile. Il documento potrebbe essere composto esclusivamente da immagini.")

                elapsed_ms = (perf_counter() - started_at) * 1000

                logger.info(
                    "PDF_EXTRACTION | phase=complete | document_id=%s | pages=%d | empty_pages=%d | chars=%d | elapsed_ms=%.2f",
                    document_id,
                    result.page_count,
                    result.empty_page_count,
                    result.total_characters,
                    elapsed_ms,
                )

                return result

        except PdfTextExtractionError:
            raise

        except Exception as exc:
            logger.exception(
                "PDF_EXTRACTION | phase=failed | document_id=%s | path=%s",
                document_id,
                resolved_path,
            )

            raise PdfTextExtractionError("Errore durante l'estrazione del testo dal PDF.") from exc
