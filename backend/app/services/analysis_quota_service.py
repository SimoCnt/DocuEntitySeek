from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.core.exceptions import AnalysisQuotaExceededError
from app.db.models import AnalysisModel
from app.repositories.analysis_quota_repository import AnalysisQuotaRepository
from app.services.analysis_quota_models import AnalysisQuotaDecision, AnalysisQuotaStatus
from app.core.logging import get_logger


logger = get_logger("analysis.quota")


class AnalysisQuotaService:
    def __init__(self, repository: AnalysisQuotaRepository) -> None:
        self.repository = repository


    def assert_can_queue(
            self, 
            *, 
            user_id: UUID, 
            now: datetime | None = None
            ) -> AnalysisQuotaDecision:
        current = now or datetime.now(timezone.utc)
        window_start = current.replace(hour=0, minute=0, second=0, microsecond=0)
        window_end = window_start + timedelta(days=1)

        locked = self.repository.lock_user_and_plan(user_id)

        if locked is None:
            raise LookupError("Utente non trovato.")

        _, plan = locked
        limit = plan.daily_analysis_limit        

        if limit is None:
            logger.info("ANALYSIS_QUOTA | phase=unlimited | user_id=%s",user_id)
            return AnalysisQuotaDecision(
                user_id=user_id,
                daily_limit=None,
                used_or_reserved=0,
                remaining_after_queue=None,
                window_start=window_start,
                window_end=window_end,
            )

        used = self.repository.count_used_or_reserved(
            user_id=user_id,
            window_start=window_start,
            window_end=window_end,
        )

        if used >= limit:
            raise AnalysisQuotaExceededError(
                daily_limit=limit,
                used=used,
                resets_at=window_end,
            )

        return AnalysisQuotaDecision(
            user_id=user_id,
            daily_limit=limit,
            used_or_reserved=used,
            remaining_after_queue=limit - used - 1,
            window_start=window_start,
            window_end=window_end,
        )


    def get_status(
            self, 
            *, 
            user_id: UUID, 
            now: datetime | None = None
            ) -> AnalysisQuotaStatus:
        current = now or datetime.now(timezone.utc)
        window_start = current.replace(hour=0, minute=0, second=0, microsecond=0)
        window_end = window_start + timedelta(days=1)

        user_and_plan = self.repository.get_user_and_plan(user_id)

        if user_and_plan is None:
            raise LookupError("Utente non trovato.")

        user, plan = user_and_plan
        limit = plan.daily_analysis_limit

        if limit is None:
            return AnalysisQuotaStatus(
                user_id=user.id,
                plan_code=plan.code,
                daily_limit=None,
                used_or_reserved=0,
                remaining=None,
                window_start=window_start,
                window_end=window_end,
            )

        used = self.repository.count_used_or_reserved(
            user_id=user_id,
            window_start=window_start,
            window_end=window_end,
        )

        return AnalysisQuotaStatus(
            user_id=user.id,
            plan_code=plan.code,
            daily_limit=limit,
            used_or_reserved=used,
            remaining=max(limit - used, 0),
            window_start=window_start,
            window_end=window_end,
        )


    @staticmethod
    def consume_on_success(*, analysis: AnalysisModel, decision: AnalysisQuotaDecision) -> None:
        if decision.is_unlimited:
            return

        if analysis.created_at is None:
            raise RuntimeError("Analysis senza created_at.")

        analysis.quota_consumed_at = analysis.created_at