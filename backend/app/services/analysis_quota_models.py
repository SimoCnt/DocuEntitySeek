"""Represent quota decisions and user-visible quota status for daily analysis limits."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AnalysisQuotaDecision:
    """Quota reservation decision at analysis submission time."""

    user_id: UUID
    daily_limit: int | None
    used_or_reserved: int
    remaining_after_queue: int | None
    window_start: datetime
    window_end: datetime

    @property
    def is_unlimited(self) -> bool:
        """Report whether the account has no daily analysis limit."""

        return self.daily_limit is None


@dataclass(frozen=True, slots=True)
class AnalysisQuotaStatus:
    """Current-user analysis quota snapshot for the frontend."""

    user_id: UUID
    plan_code: str
    daily_limit: int | None
    used_or_reserved: int
    remaining: int | None
    window_start: datetime
    window_end: datetime

    @property
    def is_unlimited(self) -> bool:
        """Report whether the plan allows unlimited daily analyses."""

        return self.daily_limit is None
