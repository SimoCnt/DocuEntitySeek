"""Fetch extraction schema versions with definitions and locate the built-in default version."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import ExtractionSchemaModel, ExtractionSchemaVersionModel


DEFAULT_BUILTIN_SCHEMA_STRUCTURE_KEY = "general_document"


class ExtractionSchemaRepository:
    """Resolve schema versions and the built-in default extraction schema."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_version(self, version_id: UUID) -> ExtractionSchemaVersionModel | None:
        """Load a schema version and associated entity/field definitions."""

        statement = (
            select(ExtractionSchemaVersionModel)
            .where(ExtractionSchemaVersionModel.id == version_id)
            .options(
                selectinload(ExtractionSchemaVersionModel.schema),
                selectinload(ExtractionSchemaVersionModel.entity_definitions),
                selectinload(ExtractionSchemaVersionModel.field_definitions),
            )
        )

        return self.session.scalar(statement)

    def get_default_builtin_version(self) -> ExtractionSchemaVersionModel | None:
        """Return the active version of the default built-in schema."""

        statement = (
            select(ExtractionSchemaVersionModel)
            .join(ExtractionSchemaModel)
            .where(
                ExtractionSchemaModel.structure_key == DEFAULT_BUILTIN_SCHEMA_STRUCTURE_KEY,
                ExtractionSchemaModel.is_builtin.is_(True),
                ExtractionSchemaModel.archived_at.is_(None),
                ExtractionSchemaVersionModel.is_active.is_(True),
            )
            .options(
                selectinload(ExtractionSchemaVersionModel.schema),
                selectinload(ExtractionSchemaVersionModel.entity_definitions),
                selectinload(ExtractionSchemaVersionModel.field_definitions),
            )
        )

        return self.session.scalar(statement)
