from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload, joinedload
from datetime import datetime, timezone

from app.db.models import AnalysisModel, ExtractedFieldModel, ExtractionSchemaVersionModel, DocumentModel
from app.domain.analysis import AnalysisStatus


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AnalysisRepository:
    def __init__(self, session: Session) -> None:
        self.session = session


    def get_latest_completed(self, document_id: UUID) -> AnalysisModel | None:
        statement = (
            select(AnalysisModel)
            .where(AnalysisModel.document_id == document_id, AnalysisModel.status == AnalysisStatus.READY.value)
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


    def create_queued(
        self,
        *,
        document_id: UUID,
        schema_version_id: UUID,
        ai_runtime_config_id: UUID,
        config: dict[str, object],
    ) -> AnalysisModel:
        analysis = AnalysisModel(
            document_id=document_id,
            schema_version_id=schema_version_id,
            ai_runtime_config_id=ai_runtime_config_id,
            status=AnalysisStatus.QUEUED.value,
            config=config,
            started_at=None,
            completed_at=None,
            error_message=None,
        )

        self.session.add(analysis)
        self.session.flush()

        return analysis


    def get_by_id(self, analysis_id: UUID) -> AnalysisModel | None:
        return self.session.scalar(
            select(AnalysisModel).where(
                AnalysisModel.id == analysis_id
            )
        )


    def mark_processing(self, analysis: AnalysisModel) -> None:
        analysis.status = AnalysisStatus.PROCESSING.value
        analysis.started_at = utc_now()
        analysis.completed_at = None
        analysis.error_message = None

        self.session.flush()


    def mark_ready(self, analysis: AnalysisModel) -> None:
        analysis.status = AnalysisStatus.READY.value
        analysis.completed_at = utc_now()
        analysis.error_message = None

        self.session.flush()


    def mark_error(
        self,
        analysis: AnalysisModel,
        *,
        error_message: str,
    ) -> None:
        analysis.status = AnalysisStatus.ERROR.value
        analysis.completed_at = utc_now()
        analysis.error_message = error_message

        self.session.flush()


    def list_for_document_and_owner(
        self,
        *,
        document_id: UUID,
        owner_user_id: UUID,
    ) -> list[AnalysisModel]:
        statement = (
            select(AnalysisModel)
            .join(DocumentModel, DocumentModel.id == AnalysisModel.document_id)
            .where(
                AnalysisModel.document_id == document_id,
                DocumentModel.owner_user_id == owner_user_id,
            )
            .order_by(AnalysisModel.created_at.desc())
        )

        return list(self.session.scalars(statement).all())


    def get_for_document_and_owner(
        self,
        *,
        analysis_id: UUID,
        document_id: UUID,
        owner_user_id: UUID,
    ) -> AnalysisModel | None:
        statement = (
            select(AnalysisModel)
            .join(DocumentModel, DocumentModel.id == AnalysisModel.document_id)
            .where(
                AnalysisModel.id == analysis_id,
                AnalysisModel.document_id == document_id,
                DocumentModel.owner_user_id == owner_user_id,
            )
        )

        return self.session.scalar(statement)


    def get_schema_version_with_definitions(self, schema_version_id: UUID) -> ExtractionSchemaVersionModel | None:
        statement = (
            select(ExtractionSchemaVersionModel)
            .options(
                joinedload(ExtractionSchemaVersionModel.schema),
                selectinload(ExtractionSchemaVersionModel.entity_definitions),
                selectinload(ExtractionSchemaVersionModel.field_definitions),
            )
            .where(ExtractionSchemaVersionModel.id == schema_version_id)
        )

        return self.session.scalar(statement)
