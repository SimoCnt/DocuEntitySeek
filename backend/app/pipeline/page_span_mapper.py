"""Map global NER and field offsets onto document pages with strict text-boundary checks."""

from time import perf_counter
from uuid import UUID

from app.core.exceptions import SpanMappingError
from app.core.logging import get_logger
from app.pipeline.field_models import StructuredExtractionResult
from app.pipeline.models import PreparedDocumentPage, PreparedDocumentText
from app.pipeline.ner_models import ViewerNerSelectionResult
from app.pipeline.page_mapping_models import FieldPageMappingResult, MappedFieldCandidate, MappedNerOccurrence, NerPageMappingResult, PageSpanCoordinates, RejectedFieldCandidate, RejectedNerCandidate, SpanMappingFailureReason


logger = get_logger("pipeline.page_mapping")


class PageSpanMapper:
    """Validate and translate global AI text spans to PDF page offsets."""

    def map_ner(
        self,
        *,
        document_id: UUID,
        document: PreparedDocumentText,
        selection: ViewerNerSelectionResult,
    ) -> NerPageMappingResult:
        """Associate valid global NER spans with a single PDF page and local offsets."""

        started_at = perf_counter()

        logger.info(
            "SPAN_MAPPING | phase=ner_start | document_id=%s | candidates=%d | pages=%d",
            document_id,
            len(selection.decisions),
            document.page_count,
        )

        mapped: list[MappedNerOccurrence] = []
        rejected: list[RejectedNerCandidate] = []

        for decision in selection.decisions:
            candidate = decision.candidate

            coordinates, reason = self._resolve_span(
                document=document,
                start=candidate.start,
                end=candidate.end,
            )

            if reason is not None:
                rejected.append(
                    RejectedNerCandidate(
                        candidate=candidate,
                        is_visible=decision.is_visible,
                        reason=reason,
                    )
                )

                logger.warning(
                    "SPAN_MAPPING | phase=ner_rejected | document_id=%s | label=%s | start=%d | end=%d | reason=%s",
                    document_id,
                    candidate.label,
                    candidate.start,
                    candidate.end,
                    reason.value,
                )

                continue

            assert coordinates is not None

            self._validate_text_mapping(
                document=document,
                coordinates=coordinates,
                global_start=candidate.start,
                global_end=candidate.end,
                expected_text=candidate.text,
            )

            mapped.append(
                MappedNerOccurrence(
                    candidate=candidate,
                    page_number=coordinates.page_number,
                    page_start=coordinates.page_start,
                    page_end=coordinates.page_end,
                    is_visible=decision.is_visible,
                )
            )

        result = NerPageMappingResult(
            mapped=tuple(mapped),
            rejected=tuple(rejected),
        )

        elapsed_ms = (perf_counter() - started_at) * 1000

        logger.info(
            "SPAN_MAPPING | phase=ner_complete | document_id=%s | mapped=%d | rejected=%d | elapsed_ms=%.2f",
            document_id,
            result.mapped_count,
            result.rejected_count,
            elapsed_ms,
        )

        return result


    def map_fields(
        self,
        *,
        document_id: UUID,
        document: PreparedDocumentText,
        result: StructuredExtractionResult,
    ) -> FieldPageMappingResult:
        """Associate structured field candidates with pages; reject invalid spans."""

        started_at = perf_counter()

        logger.info(
            "SPAN_MAPPING | phase=fields_start | document_id=%s | candidates=%d | pages=%d",
            document_id,
            result.total_candidates,
            document.page_count,
        )

        mapped: list[MappedFieldCandidate] = []
        rejected: list[RejectedFieldCandidate] = []

        for candidate in result.candidates:
            coordinates, reason = self._resolve_span(
                document=document,
                start=candidate.start,
                end=candidate.end,
            )

            if reason is not None:
                rejected.append(
                    RejectedFieldCandidate(
                        candidate=candidate,
                        reason=reason,
                    )
                )

                logger.warning(
                    "SPAN_MAPPING | phase=field_rejected | document_id=%s | field_key=%s | start=%d | end=%d | reason=%s",
                    document_id,
                    candidate.field_key,
                    candidate.start,
                    candidate.end,
                    reason.value,
                )

                continue

            assert coordinates is not None

            self._validate_text_mapping(
                document=document,
                coordinates=coordinates,
                global_start=candidate.start,
                global_end=candidate.end,
                expected_text=candidate.value,
            )

            mapped.append(
                MappedFieldCandidate(
                    candidate=candidate,
                    page_number=coordinates.page_number,
                    page_start=coordinates.page_start,
                    page_end=coordinates.page_end,
                )
            )

        mapping = FieldPageMappingResult(
            mapped=tuple(mapped),
            rejected=tuple(rejected),
        )

        elapsed_ms = (perf_counter() - started_at) * 1000

        logger.info(
            "SPAN_MAPPING | phase=fields_complete | document_id=%s | mapped=%d | rejected=%d | elapsed_ms=%.2f",
            document_id,
            mapping.mapped_count,
            mapping.rejected_count,
            elapsed_ms,
        )

        return mapping


    def _resolve_span(
        self,
        *,
        document: PreparedDocumentText,
        start: int,
        end: int,
    ) -> tuple[PageSpanCoordinates | None, SpanMappingFailureReason | None]:
        """Find the page containing an entire global span, or return a failure reason."""

        if start < 0 or end <= start or end > len(document.text):
            raise SpanMappingError(f"Span globale non valido: [{start}, {end}).")

        start_page = self._find_page_for_position(pages=document.pages, position=start)
        end_page = self._find_page_for_position(pages=document.pages, position=end - 1)

        if start_page is None:
            return None, SpanMappingFailureReason.START_IN_PAGE_SEPARATOR

        if end_page is None:
            return None, SpanMappingFailureReason.END_IN_PAGE_SEPARATOR

        if start_page.page_number != end_page.page_number:
            return None, SpanMappingFailureReason.CROSS_PAGE

        return (
            PageSpanCoordinates(
                page_number=start_page.page_number,
                page_start=start - start_page.global_start,
                page_end=end - start_page.global_start,
            ),
            None,
        )


    @staticmethod
    def _find_page_for_position(
        *,
        pages: tuple[PreparedDocumentPage, ...],
        position: int,
    ) -> PreparedDocumentPage | None:
        """Find the source PDF page containing the global character offset."""

        for page in pages:
            if page.global_start <= position < page.global_end:
                return page

        return None


    def _validate_text_mapping(
        self,
        *,
        document: PreparedDocumentText,
        coordinates: PageSpanCoordinates,
        global_start: int,
        global_end: int,
        expected_text: str,
    ) -> None:
        """Ensure the mapped page slice matches the candidate's source text exactly."""

        page = next(
            (item for item in document.pages if item.page_number == coordinates.page_number),
            None,
        )

        if page is None:
            raise SpanMappingError(f"Pagina {coordinates.page_number} non trovata.")

        global_text = document.text[global_start:global_end]
        local_text = page.text[coordinates.page_start:coordinates.page_end]

        if global_text != expected_text:
            raise SpanMappingError("Il testo dello span globale non corrisponde al candidato.")

        if local_text != expected_text:
            raise SpanMappingError("Il testo dello span locale non corrisponde al candidato.")
