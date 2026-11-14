from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import ExtractionSchemaModel, ExtractionSchemaVersionModel


class ExtractionSchemaRepository:
    def __init__(self, session: Session) -> None:
        self.session = session


    def get_version(self, version_id: UUID) -> ExtractionSchemaVersionModel | None:
        statement = (
            select(ExtractionSchemaVersionModel)
            .where(ExtractionSchemaVersionModel.id == version_id)
            .options(
                selectinload(ExtractionSchemaVersionModel.schema),
                selectinload(ExtractionSchemaVersionModel.entity_definitions),
                selectinload(ExtractionSchemaVersionModel.field_definitions)
            )
        )

        return self.session.scalar(statement)


    def get_default_builtin_version(self) -> ExtractionSchemaVersionModel | None:
        statement = (
            select(ExtractionSchemaVersionModel)
            .join(ExtractionSchemaModel)
            .where(
                ExtractionSchemaModel.is_builtin.is_(True),
                ExtractionSchemaVersionModel.is_active.is_(True)
            )
            .options(
                selectinload(ExtractionSchemaVersionModel.schema),
                selectinload(ExtractionSchemaVersionModel.entity_definitions),
                selectinload(ExtractionSchemaVersionModel.field_definitions)
            )
        )

        return self.session.scalar(statement)