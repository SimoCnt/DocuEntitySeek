"""Implement user-owned schema creation, listing, editing, archival, and duplication."""

from uuid import UUID, uuid4
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.db.models import EntityDefinitionModel, ExtractionSchemaModel, ExtractionSchemaVersionModel, FieldDefinitionModel
from app.repositories.custom_schema_repository import CustomSchemaRepository
from app.services.custom_schema_models import CustomEntityDefinitionResult, CustomFieldDefinitionResult, CustomSchemaCreateCommand, CustomSchemaResult, CustomSchemaSummary
from app.services.schema_access_service import SchemaAccessService
from app.core.exceptions import CustomSchemaNameConflictError, ExtractionSchemaNotFoundError, CustomSchemaArchivedError


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
    """Manage lifecycle and versioning of user-owned extraction schemas."""

    def __init__(self, *, session: Session, schema_access_service: SchemaAccessService) -> None:
        self.session = session
        self.repository = CustomSchemaRepository(session)
        self.schema_access_service = schema_access_service


    def create(self, *, user_id: UUID, command: CustomSchemaCreateCommand) -> CustomSchemaResult:
        """Validate and persist a new custom extraction schema and its initial version."""

        self.schema_access_service.assert_custom_schemas_enabled(user_id=user_id)

        if self.repository.name_exists_for_owner(user_id=user_id, name=command.name):
            raise CustomSchemaNameConflictError("Esiste già uno schema personalizzato con questo nome.")

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
                archived_at=schema.archived_at,
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
        """List active and archived schema summaries for the requesting owner."""

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
                archived_at=version.schema.archived_at
            )
            for version in versions
        ]


    def get_owned(self, *, user_id: UUID, schema_id: UUID) -> CustomSchemaResult:
        """Load a complete user-owned schema with versioned definitions."""

        self.schema_access_service.assert_custom_schemas_enabled(user_id=user_id)

        version = self.repository.get_owned_active_version_with_definitions(
            user_id=user_id,
            schema_id=schema_id,
        )

        if version is None:
            raise ExtractionSchemaNotFoundError("Schema di estrazione non trovato.")

        return CustomSchemaResult(
            schema_id=version.schema.id,
            schema_version_id=version.id,
            name=version.schema.name,
            domain=version.schema.domain,
            version=version.version,
            created_at=version.schema.created_at,
            archived_at=version.schema.archived_at,
            entities=tuple(
                CustomEntityDefinitionResult(
                    id=entity.id,
                    label=entity.label,
                    description=entity.description,
                    color=entity.color,
                    sort_order=entity.sort_order,
                )
                for entity in sorted(version.entity_definitions, key=lambda item: item.sort_order)
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
                for field in sorted(version.field_definitions, key=lambda item: item.sort_order)
            ),
        )


    def update(
        self,
        *,
        user_id: UUID,
        schema_id: UUID,
        command: CustomSchemaCreateCommand,
    ) -> CustomSchemaResult:
        """Create a new schema version without rewriting existing historical versions."""

        self.schema_access_service.assert_custom_schemas_enabled(user_id=user_id)

        try:
            schema = self.repository.get_owned_schema_for_update(
                user_id=user_id,
                schema_id=schema_id,
            )

            if schema is None:
                raise ExtractionSchemaNotFoundError("Schema di estrazione non trovato.")

            if schema.archived_at is not None:
                raise CustomSchemaArchivedError("Uno schema archiviato non può essere modificato.")

            if self.repository.name_exists_for_owner(
                user_id=user_id,
                name=command.name,
                exclude_schema_id=schema.id,
            ):
                raise CustomSchemaNameConflictError("Esiste già uno schema personalizzato con questo nome.")

            active_version = self.repository.get_active_version(schema_id=schema.id)

            if active_version is None:
                raise ExtractionSchemaNotFoundError("Lo schema non possiede una versione attiva.")

            next_version_number = self.repository.get_max_version_number(schema_id=schema.id) + 1
            active_version.is_active = False
            new_version_id = uuid4()

            new_version = ExtractionSchemaVersionModel(
                id=new_version_id,
                schema_id=schema.id,
                version=next_version_number,
                is_active=True,
            )

            entities = [
                EntityDefinitionModel(
                    schema_version_id=new_version_id,
                    label=entity.label,
                    description=entity.description,
                    color=ENTITY_COLOR_PALETTE[index % len(ENTITY_COLOR_PALETTE)],
                    sort_order=index,
                )
                for index, entity in enumerate(command.entities)
            ]

            fields = [
                FieldDefinitionModel(
                    schema_version_id=new_version_id,
                    field_key=field.field_key,
                    label=field.label,
                    description=field.description,
                    data_type="string",
                    is_required=field.is_required,
                    sort_order=index,
                )
                for index, field in enumerate(command.fields)
            ]

            schema.name = command.name
            schema.domain = command.domain

            self.repository.add_version(new_version)
            self.repository.add_entities(entities)
            self.repository.add_fields(fields)
            self.repository.flush()

            result = CustomSchemaResult(
                schema_id=schema.id,
                schema_version_id=new_version.id,
                name=schema.name,
                domain=schema.domain,
                version=new_version.version,
                created_at=schema.created_at,
                archived_at=schema.archived_at,
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


    def archive(
            self, 
            *, 
            user_id: UUID, 
            schema_id: UUID
            ) -> datetime:
        """Mark a schema archived while preserving existing references."""

        self.schema_access_service.assert_custom_schemas_enabled(user_id=user_id)

        try:
            schema = self.repository.get_owned_schema_for_update(user_id=user_id, schema_id=schema_id)

            if schema is None:
                raise ExtractionSchemaNotFoundError("Schema di estrazione non trovato.")

            if schema.archived_at is None:
                schema.archived_at = datetime.now(timezone.utc)

            archived_at = schema.archived_at
            self.session.commit()

            return archived_at

        except Exception:
            self.session.rollback()
            raise


    def duplicate(self, *, user_id: UUID, schema_id: UUID, name: str) -> CustomSchemaResult:
        """Copy definitions into a new user-owned schema with its own version history."""

        self.schema_access_service.assert_custom_schemas_enabled(user_id=user_id)

        if self.repository.name_exists_for_owner(user_id=user_id, name=name):
            raise CustomSchemaNameConflictError("Esiste già uno schema personalizzato con questo nome.")

        source_version = self.repository.get_owned_active_version_with_definitions(
            user_id=user_id,
            schema_id=schema_id,
        )

        if source_version is None:
            raise ExtractionSchemaNotFoundError("Schema di estrazione non trovato.")

        new_schema_id = uuid4()
        new_version_id = uuid4()

        schema = ExtractionSchemaModel(
            id=new_schema_id,
            owner_user_id=user_id,
            structure_key=f"custom_{new_schema_id.hex}",
            name=name,
            domain=source_version.schema.domain,
            is_builtin=False,
        )

        version = ExtractionSchemaVersionModel(
            id=new_version_id,
            schema_id=new_schema_id,
            version=1,
            is_active=True,
        )

        source_entities = sorted(source_version.entity_definitions, key=lambda item: item.sort_order)

        entities = [
            EntityDefinitionModel(
                schema_version_id=new_version_id,
                label=entity.label,
                description=entity.description,
                color=entity.color,
                sort_order=index,
            )
            for index, entity in enumerate(source_entities)
        ]

        source_fields = sorted(source_version.field_definitions, key=lambda item: item.sort_order)

        fields = [
            FieldDefinitionModel(
                schema_version_id=new_version_id,
                field_key=field.field_key,
                label=field.label,
                description=field.description,
                data_type=field.data_type,
                is_required=field.is_required,
                sort_order=index,
            )
            for index, field in enumerate(source_fields)
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
                archived_at=schema.archived_at,
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
