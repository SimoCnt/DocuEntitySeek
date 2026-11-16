from datetime import datetime, timezone
from unittest.mock import Mock
from uuid import uuid4
import pytest

from app.services.analysis_quota_service import AnalysisQuotaService


@pytest.mark.unit
def test_base_user_can_queue_when_under_limit() -> None:
    user = Mock()
    user.id = uuid4()

    plan = Mock()
    plan.daily_analysis_limit = 5

    repository = Mock()
    repository.lock_user_and_plan.return_value = (user, plan)
    repository.count_used_or_reserved.return_value = 3

    service = AnalysisQuotaService(repository)

    decision = service.assert_can_queue(
        user_id=user.id,
        now=datetime(2026, 11, 16, 12, 0, tzinfo=timezone.utc),
    )

    assert decision.daily_limit == 5
    assert decision.used_or_reserved == 3
    assert decision.remaining_after_queue == 1
    assert decision.is_unlimited is False


from app.core.exceptions import AnalysisQuotaExceededError


@pytest.mark.unit
def test_base_user_cannot_queue_at_limit() -> None:
    user = Mock()
    user.id = uuid4()

    plan = Mock()
    plan.daily_analysis_limit = 5

    repository = Mock()
    repository.lock_user_and_plan.return_value = (user, plan)
    repository.count_used_or_reserved.return_value = 5

    service = AnalysisQuotaService(repository)

    with pytest.raises(AnalysisQuotaExceededError) as exc_info:
        service.assert_can_queue(user_id=user.id)

    assert exc_info.value.daily_limit == 5
    assert exc_info.value.used == 5


@pytest.mark.unit
def test_premium_user_is_unlimited() -> None:
    user = Mock()
    user.id = uuid4()

    plan = Mock()
    plan.daily_analysis_limit = None

    repository = Mock()
    repository.lock_user_and_plan.return_value = (user, plan)

    service = AnalysisQuotaService(repository)
    decision = service.assert_can_queue(user_id=user.id)

    assert decision.is_unlimited is True
    assert decision.daily_limit is None
    assert decision.remaining_after_queue is None

    repository.count_used_or_reserved.assert_not_called()


@pytest.mark.unit
def test_base_success_consumes_quota_at_analysis_creation_time() -> None:
    created_at = datetime(2026, 11, 16, 23, 59, tzinfo=timezone.utc)

    analysis = Mock()
    analysis.created_at = created_at
    analysis.quota_consumed_at = None

    decision = Mock()
    decision.is_unlimited = False

    AnalysisQuotaService.consume_on_success(
        analysis=analysis,
        decision=decision,
    )

    assert analysis.quota_consumed_at == created_at


@pytest.mark.unit
def test_premium_success_does_not_set_quota_consumed_at() -> None:
    analysis = Mock()
    analysis.quota_consumed_at = None

    decision = Mock()
    decision.is_unlimited = True

    AnalysisQuotaService.consume_on_success(
        analysis=analysis,
        decision=decision,
    )

    assert analysis.quota_consumed_at is None