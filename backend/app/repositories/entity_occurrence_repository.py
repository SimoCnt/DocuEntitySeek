from decimal import Decimal
from uuid import UUID
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.models import EntityOccurrenceModel
from app.pipeline.page_mapping_models import MappedNerOccurrence


class EntityOccurrenceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session


    def replace_for_analysis(
        self,
        *,
        analysis_id: UUID,
        occurrences: tuple[MappedNerOccurrence, ...],
    ) -> list[EntityOccurrenceModel]:
        self.session.execute(
            delete(EntityOccurrenceModel).where(EntityOccurrenceModel.analysis_id == analysis_id)
        )

        models = [
            EntityOccurrenceModel(
                analysis_id=analysis_id,
                label=occurrence.candidate.label,
                text=occurrence.candidate.text,
                confidence=Decimal(str(occurrence.candidate.confidence)),
                global_start=occurrence.candidate.start,
                global_end=occurrence.candidate.end,
                page=occurrence.page_number,
                page_start=occurrence.page_start,
                page_end=occurrence.page_end,
                is_visible=occurrence.is_visible,
            )
            for occurrence in occurrences
        ]

        self.session.add_all(models)
        self.session.flush()

        return models


    def list_for_analysis(self, analysis_id: UUID) -> list[EntityOccurrenceModel]:
        statement = (
            select(EntityOccurrenceModel)
            .where(EntityOccurrenceModel.analysis_id == analysis_id)
            .order_by(
                EntityOccurrenceModel.page,
                EntityOccurrenceModel.page_start,
                EntityOccurrenceModel.label,
            )
        )

        return list(self.session.scalars(statement).all())