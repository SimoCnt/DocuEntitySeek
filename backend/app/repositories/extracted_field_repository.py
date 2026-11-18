from decimal import Decimal
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.models import ExtractedFieldModel, FieldCandidateModel
from app.pipeline.field_resolution_models import FieldResolutionResult


class ExtractedFieldRepository:
    def __init__(self, session: Session) -> None:
        self.session = session


    def replace_for_analysis(self, *, analysis_id: UUID, result: FieldResolutionResult) -> list[ExtractedFieldModel]:
        self.session.execute(
            delete(ExtractedFieldModel).where(ExtractedFieldModel.analysis_id == analysis_id)
        )

        models = [
            ExtractedFieldModel(
                analysis_id=analysis_id,
                field_key=field.field_key,
                value_text=field.value,
                status=field.status.value,
                confidence=Decimal(str(field.confidence)) if field.confidence is not None else None,
                page=field.page_number,
                global_start=field.global_start,
                global_end=field.global_end,
            )
            for field in result.fields
        ]

        self.session.add_all(models)
        self.session.flush()

        candidates: list[FieldCandidateModel] = []

        for field, model in zip(result.fields, models, strict=True):
            candidates.extend(
                FieldCandidateModel(
                    extracted_field_id=model.id,
                    value_text=ranked.candidate.value,
                    confidence=Decimal(str(ranked.candidate.confidence)),
                    page=ranked.page_number,
                    global_start=ranked.candidate.start,
                    global_end=ranked.candidate.end,
                    candidate_rank=ranked.rank,
                )
                for ranked in field.candidates
            )

        self.session.add_all(candidates)
        self.session.flush()

        return models

    def list_for_analysis(self, analysis_id: UUID) -> list[ExtractedFieldModel]:
        statement = (
            select(ExtractedFieldModel)
            .where(ExtractedFieldModel.analysis_id == analysis_id)
            .order_by(ExtractedFieldModel.field_key)
        )

        return list(self.session.scalars(statement).all())