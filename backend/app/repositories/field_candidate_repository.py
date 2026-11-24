"""Load ranked field candidates for extracted fields."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import FieldCandidateModel


class FieldCandidateRepository:
    """Fetch candidate values for one or more extracted fields."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_for_extracted_fields(self, extracted_field_ids: list[UUID]) -> list[FieldCandidateModel]:
        """Load ranked candidates for the specified extracted-field IDs."""

        if not extracted_field_ids:
            return []

        statement = (
            select(FieldCandidateModel)
            .where(FieldCandidateModel.extracted_field_id.in_(extracted_field_ids))
            .order_by(FieldCandidateModel.extracted_field_id, FieldCandidateModel.candidate_rank)
        )

        return list(self.session.scalars(statement).all())
