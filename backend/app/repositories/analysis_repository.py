
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import AnalysisModel, ExtractedFieldModel, ExtractionSchemaVersionModel


class AnalysisRepository:
    def __init__(self, session: Session) -> None:
        self.session = session


    def get_latest_completed(self, document_id: UUID) -> AnalysisModel | None:
        statement = (
            select(AnalysisModel)
            .where(AnalysisModel.document_id == document_id, AnalysisModel.status == "COMPLETED")
            .order_by(AnalysisModel.created_at.desc())
            .limit(1)
            .options(
                selectinload(AnalysisModel.entity_occurrences),
                selectinload(AnalysisModel.extracted_fields).selectinload(ExtractedFieldModel.candidates),
                selectinload(AnalysisModel.schema_version).selectinload(ExtractionSchemaVersionModel.entity_definitions),
                selectinload(AnalysisModel.schema_version).selectinload(ExtractionSchemaVersionModel.field_definitions),
            )
        )
        return self.session.scalar(statement)
