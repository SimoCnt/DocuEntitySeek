from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.db.models import EntityDefinitionModel, ExtractionSchemaModel, ExtractionSchemaVersionModel, FieldDefinitionModel


class CustomSchemaRepository:
    def __init__(self, session: Session) -> None:
        self.session = session


    def add_schema(self, schema: ExtractionSchemaModel) -> None:
        self.session.add(schema)


    def add_version(self, version: ExtractionSchemaVersionModel) -> None:
        self.session.add(version)


    def add_entities(self, entities: list[EntityDefinitionModel]) -> None:
        self.session.add_all(entities)


    def add_fields(self, fields: list[FieldDefinitionModel]) -> None:
        self.session.add_all(fields)


    def flush(self) -> None:
        self.session.flush()


    def list_active_owned_versions(
        self,
        *,
        user_id: UUID,
    ) -> list[ExtractionSchemaVersionModel]:
        statement = (
            select(ExtractionSchemaVersionModel)
            .join(
                ExtractionSchemaModel,
                ExtractionSchemaModel.id == ExtractionSchemaVersionModel.schema_id,
            )
            .options(
                joinedload(ExtractionSchemaVersionModel.schema),
                selectinload(ExtractionSchemaVersionModel.entity_definitions),
                selectinload(ExtractionSchemaVersionModel.field_definitions),
            )
            .where(
                ExtractionSchemaModel.owner_user_id == user_id,
                ExtractionSchemaModel.is_builtin.is_(False),
                ExtractionSchemaVersionModel.is_active.is_(True),
            )
            .order_by(
                ExtractionSchemaModel.created_at.desc(),
            )
        )

        return list(
            self.session.scalars(statement).all()
        )