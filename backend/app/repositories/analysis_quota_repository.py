"""Read and lock user-plan rows and count analyses reserved or consumed in a quota window."""

from datetime import datetime
from uuid import UUID
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.db.models import AnalysisModel, DocumentModel, PlanModel, UserModel
from app.domain.analysis import AnalysisStatus


class AnalysisQuotaRepository:
    """Perform quota window queries and plan-row locking in PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self.session = session


    def get_user_and_plan(self, user_id: UUID) -> tuple[UserModel, PlanModel] | None:
        """Fetch account and plan metadata used to display the current quota."""

        statement = (
            select(UserModel, PlanModel)
            .join(PlanModel, PlanModel.code == UserModel.plan_code)
            .where(UserModel.id == user_id)
        )

        row = self.session.execute(statement).one_or_none()

        return (row[0], row[1]) if row is not None else None


    def lock_user_and_plan(self, user_id: UUID) -> tuple[UserModel, PlanModel] | None:
        """Lock the account row before checking quota reservations for concurrency safety."""

        statement = (
            select(UserModel, PlanModel)
            .join(PlanModel, PlanModel.code == UserModel.plan_code)
            .where(UserModel.id == user_id)
            .with_for_update(of=UserModel)
        )

        row = self.session.execute(statement).one_or_none()
        
        return (row[0], row[1]) if row is not None else None


    def count_used_or_reserved(
        self,
        *,
        user_id: UUID,
        window_start: datetime,
        window_end: datetime,
    ) -> int:
        """Count analyses that consume or reserve quota within a UTC window."""

        consumed = and_(
            AnalysisModel.quota_consumed_at.is_not(None),
            AnalysisModel.quota_consumed_at >= window_start,
            AnalysisModel.quota_consumed_at < window_end,
        )

        reserved = and_(
            AnalysisModel.quota_consumed_at.is_(None),
            AnalysisModel.status.in_((AnalysisStatus.QUEUED.value, AnalysisStatus.PROCESSING.value)),
            AnalysisModel.created_at >= window_start,
            AnalysisModel.created_at < window_end,
        )

        statement = (
            select(func.count(AnalysisModel.id))
            .join(DocumentModel, DocumentModel.id == AnalysisModel.document_id)
            .where(
                DocumentModel.owner_user_id == user_id,
                or_(consumed, reserved),
            )
        )

        return int(self.session.scalar(statement) or 0)
