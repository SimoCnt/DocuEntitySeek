from uuid import UUID
from sqlalchemy import select, func
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


    def get_owned_schema_for_update(
            self, 
            *, 
            user_id: 
            UUID, 
            schema_id: UUID
            ) -> ExtractionSchemaModel | None:
        statement = (
            select(ExtractionSchemaModel)
            .where(
                ExtractionSchemaModel.id == schema_id,
                ExtractionSchemaModel.owner_user_id == user_id,
                ExtractionSchemaModel.is_builtin.is_(False),
            )
            .with_for_update()
        )

        return self.session.scalar(statement)


    def get_active_version(
        self,
        *,
        schema_id: UUID,
    ) -> ExtractionSchemaVersionModel | None:
        statement = (
            select(ExtractionSchemaVersionModel)
            .where(
                ExtractionSchemaVersionModel.schema_id == schema_id,
                ExtractionSchemaVersionModel.is_active.is_(True),
            )
        )

        return self.session.scalar(statement)


    def get_max_version_number(self, *, schema_id: UUID) -> int:
        statement = select(func.max(ExtractionSchemaVersionModel.version)).where(ExtractionSchemaVersionModel.schema_id == schema_id)

        return self.session.scalar(statement) or 0


    def name_exists_for_owner(
        self,
        *,
        user_id: UUID,
        name: str,
        exclude_schema_id: UUID | None = None,
    ) -> bool:
        statement = select(ExtractionSchemaModel.id).where(
            ExtractionSchemaModel.owner_user_id == user_id,
            func.lower(ExtractionSchemaModel.name) == name.lower(),
        )

        if exclude_schema_id is not None:
            statement = statement.where(ExtractionSchemaModel.id != exclude_schema_id)

        return self.session.scalar(statement) is not None


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


    def get_owned_active_version_with_definitions(
        self,
        *,
        user_id: UUID,
        schema_id: UUID,
    ) -> ExtractionSchemaVersionModel | None:
        statement = (
            select(ExtractionSchemaVersionModel)
            .join(ExtractionSchemaModel, ExtractionSchemaModel.id == ExtractionSchemaVersionModel.schema_id)
            .options(
                joinedload(ExtractionSchemaVersionModel.schema),
                selectinload(ExtractionSchemaVersionModel.entity_definitions),
                selectinload(ExtractionSchemaVersionModel.field_definitions),
            )
            .where(
                ExtractionSchemaModel.id == schema_id,
                ExtractionSchemaModel.owner_user_id == user_id,
                ExtractionSchemaModel.is_builtin.is_(False),
                ExtractionSchemaVersionModel.is_active.is_(True),
            )
        )

        return self.session.scalar(statement)