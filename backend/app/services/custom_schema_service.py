from uuid import UUID, uuid4
from sqlalchemy.orm import Session

from app.db.models import EntityDefinitionModel, ExtractionSchemaModel, ExtractionSchemaVersionModel, FieldDefinitionModel
from app.repositories.custom_schema_repository import CustomSchemaRepository
from app.services.custom_schema_models import CustomEntityDefinitionResult, CustomFieldDefinitionResult, CustomSchemaCreateCommand, CustomSchemaResult, CustomSchemaSummary
from app.services.schema_access_service import SchemaAccessService


ENTITY_COLOR_PALETTE = (
    "#2563EB",
    "#7C3AED",
    "#DB2777",
    "#DC2626",
    "#EA580C",
    "#CA8A04",
    "#16A34A",
    "#0891B2",
    "#4F46E5",
    "#9333EA",
)


class CustomSchemaService:
    def __init__(self, *, session: Session, schema_access_service: SchemaAccessService) -> None:
        self.session = session
        self.repository = CustomSchemaRepository(session)
        self.schema_access_service = schema_access_service


    def create(self, *, user_id: UUID, command: CustomSchemaCreateCommand) -> CustomSchemaResult:
        self.schema_access_service.assert_custom_schemas_enabled(user_id=user_id)

        schema_id = uuid4()
        schema_version_id = uuid4()

        schema = ExtractionSchemaModel(
            id=schema_id,
            owner_user_id=user_id,
            structure_key=f"custom_{schema_id.hex}",
            name=command.name,
            domain=command.domain,
            is_builtin=False,
        )

        version = ExtractionSchemaVersionModel(
            id=schema_version_id,
            schema_id=schema_id,
            version=1,
            is_active=True,
        )

        entities = [
            EntityDefinitionModel(
                schema_version_id=schema_version_id,
                label=entity.label,
                description=entity.description,
                color=ENTITY_COLOR_PALETTE[index % len(ENTITY_COLOR_PALETTE)],
                sort_order=index,
            )
            for index, entity in enumerate(command.entities)
        ]

        fields = [
            FieldDefinitionModel(
                schema_version_id=schema_version_id,
                field_key=field.field_key,
                label=field.label,
                description=field.description,
                data_type="string",
                is_required=field.is_required,
                sort_order=index,
            )
            for index, field in enumerate(command.fields)
        ]

        try:
            self.repository.add_schema(schema)
            self.repository.add_version(version)
            self.repository.add_entities(entities)
            self.repository.add_fields(fields)
            self.repository.flush()

            result = CustomSchemaResult(
                schema_id=schema.id,
                schema_version_id=version.id,
                name=schema.name,
                domain=schema.domain,
                version=version.version,
                created_at=schema.created_at,
                entities=tuple(
                    CustomEntityDefinitionResult(
                        id=entity.id,
                        label=entity.label,
                        description=entity.description,
                        color=entity.color,
                        sort_order=entity.sort_order,
                    )
                    for entity in entities
                ),
                fields=tuple(
                    CustomFieldDefinitionResult(
                        id=field.id,
                        field_key=field.field_key,
                        label=field.label,
                        description=field.description,
                        data_type=field.data_type,
                        is_required=field.is_required,
                        sort_order=field.sort_order,
                    )
                    for field in fields
                ),
            )

            self.session.commit()
            return result

        except Exception:
            self.session.rollback()
            raise


    def list_owned(self, *, user_id: UUID) -> list[CustomSchemaSummary]:
        self.schema_access_service.assert_custom_schemas_enabled(user_id=user_id)

        versions = self.repository.list_active_owned_versions(user_id=user_id)

        return [
            CustomSchemaSummary(
                schema_id=version.schema.id,
                schema_version_id=version.id,
                name=version.schema.name,
                domain=version.schema.domain,
                version=version.version,
                entity_count=len(version.entity_definitions),
                field_count=len(version.field_definitions),
                created_at=version.schema.created_at,
            )
            for version in versions
        ]