from time import perf_counter
from uuid import UUID

from app.core.logging import get_logger
from app.pipeline.models import PdfExtractionResult, PreparedDocumentPage, PreparedDocumentText


logger = get_logger("pipeline.provenance")

TEXT_LAYOUT_VERSION = "page-join-v1"
PAGE_SEPARATOR = "\n\n"


class DocumentProvenanceBuilder:
    def build(
            self, 
            *, 
            document_id: UUID, 
            extraction: PdfExtractionResult
            ) -> PreparedDocumentText:
        started_at = perf_counter()

        logger.info(
            "PROVENANCE | phase=start | document_id=%s | pages=%d",
            document_id,
            extraction.page_count,
        )

        parts: list[str] = []
        prepared_pages: list[PreparedDocumentPage] = []
        cursor = 0

        for index, page in enumerate(extraction.pages):
            global_start = cursor

            parts.append(page.text)
            cursor += len(page.text)

            global_end = cursor

            prepared_page = PreparedDocumentPage(
                page_number=page.page_number,
                text=page.text,
                global_start=global_start,
                global_end=global_end,
            )

            prepared_pages.append(prepared_page)

            logger.debug(
                "PROVENANCE | phase=page_mapped | document_id=%s | page=%d | global_start=%d | global_end=%d | chars=%d",
                document_id,
                page.page_number,
                global_start,
                global_end,
                len(page.text),
            )

            is_last_page = index == len(extraction.pages) - 1

            if not is_last_page:
                parts.append(PAGE_SEPARATOR)
                cursor += len(PAGE_SEPARATOR)

        global_text = "".join(parts)

        result = PreparedDocumentText(
            text=global_text,
            pages=tuple(prepared_pages),
            layout_version=TEXT_LAYOUT_VERSION,
        )

        self._validate(document_id=document_id, result=result)

        elapsed_ms = (perf_counter() - started_at) * 1000

        logger.info(
            "PROVENANCE | phase=complete | document_id=%s | pages=%d | global_chars=%d | layout=%s | elapsed_ms=%.2f",
            document_id,
            result.page_count,
            result.total_characters,
            result.layout_version,
            elapsed_ms,
        )

        return result


    def _validate(
            self, 
            *, 
            document_id: UUID, 
            result: PreparedDocumentText
            ) -> None:
        for page in result.pages:
            reconstructed = result.text[page.global_start:page.global_end]

            if reconstructed != page.text:
                logger.error(
                    "PROVENANCE | phase=validation_failed | document_id=%s | page=%d | global_start=%d | global_end=%d",
                    document_id,
                    page.page_number,
                    page.global_start,
                    page.global_end,
                )

                raise RuntimeError("Gli offset globali della pagina non corrispondono al testo.")

        logger.debug("PROVENANCE | phase=validation_complete | document_id=%s", document_id)