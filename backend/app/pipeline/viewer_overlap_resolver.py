from time import perf_counter
from uuid import UUID

from app.core.logging import get_logger
from app.pipeline.ner_models import NerCandidate, NerExtractionResult, ViewerNerDecision, ViewerNerSelectionResult


logger = get_logger("pipeline.viewer")


class ViewerOverlapResolver:
    def resolve(self, *, document_id: UUID, result: NerExtractionResult) -> ViewerNerSelectionResult:
        started_at = perf_counter()

        logger.info(
            "VIEWER_OVERLAP | phase=start | document_id=%s | candidates=%d",
            document_id,
            result.total_candidates,
        )

        ranked = sorted(result.candidates, key=self._ranking_key)
        selected: list[NerCandidate] = []
        decisions_by_key: dict[tuple[str, int, int], ViewerNerDecision] = {}

        for candidate in ranked:
            blocker = self._find_blocker(candidate=candidate, selected=selected)

            if blocker is None:
                selected.append(candidate)

                decisions_by_key[self._candidate_key(candidate)] = ViewerNerDecision(candidate=candidate, is_visible=True)

                logger.debug(
                    "VIEWER_OVERLAP | phase=selected | document_id=%s | label=%s | start=%d | end=%d | confidence=%.4f",
                    document_id,
                    candidate.label,
                    candidate.start,
                    candidate.end,
                    candidate.confidence,
                )

                continue

            decisions_by_key[self._candidate_key(candidate)] = ViewerNerDecision(
                candidate=candidate,
                is_visible=False,
                blocked_by=blocker,
            )

            logger.debug(
                "VIEWER_OVERLAP | phase=hidden_overlap | document_id=%s | label=%s | start=%d | end=%d | confidence=%.4f | blocked_by_label=%s | blocked_by_start=%d | blocked_by_end=%d | blocked_by_confidence=%.4f",
                document_id,
                candidate.label,
                candidate.start,
                candidate.end,
                candidate.confidence,
                blocker.label,
                blocker.start,
                blocker.end,
                blocker.confidence,
            )

        decisions = tuple(
            decisions_by_key[self._candidate_key(candidate)]
            for candidate in sorted(result.candidates, key=lambda item: (item.start, item.end, item.label))
        )

        selection = ViewerNerSelectionResult(decisions=decisions)
        elapsed_ms = (perf_counter() - started_at) * 1000

        logger.info(
            "VIEWER_OVERLAP | phase=complete | document_id=%s | candidates=%d | visible=%d | hidden=%d | elapsed_ms=%.2f",
            document_id,
            result.total_candidates,
            selection.visible_count,
            selection.hidden_count,
            elapsed_ms,
        )

        return selection


    @staticmethod
    def _candidate_key(candidate: NerCandidate) -> tuple[str, int, int]:
        return (candidate.label, candidate.start, candidate.end)


    @staticmethod
    def _ranking_key(candidate: NerCandidate) -> tuple[float, int, int, str]:
        return (-candidate.confidence, -candidate.length, candidate.start, candidate.label)


    def _find_blocker(self, *, candidate: NerCandidate, selected: list[NerCandidate]) -> NerCandidate | None:
        for visible in selected:
            if self._overlaps(candidate, visible):
                return visible

        return None


    @staticmethod
    def _overlaps(first: NerCandidate, second: NerCandidate) -> bool:
        return first.start < second.end and second.start < first.end