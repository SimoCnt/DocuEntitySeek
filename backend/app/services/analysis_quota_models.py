from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AnalysisQuotaDecision:
    user_id: UUID
    daily_limit: int | None
    used_or_reserved: int
    remaining_after_queue: int | None
    window_start: datetime
    window_end: datetime

    @property
    def is_unlimited(self) -> bool:
        return self.daily_limit is None


@dataclass(frozen=True, slots=True)
class AnalysisQuotaStatus:
    user_id: UUID
    plan_code: str
    daily_limit: int | None
    used_or_reserved: int
    remaining: int | None
    window_start: datetime
    window_end: datetime

    @property
    def is_unlimited(self) -> bool:
        return self.daily_limit is None