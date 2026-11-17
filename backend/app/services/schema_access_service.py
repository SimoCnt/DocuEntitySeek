from uuid import UUID

from app.core.exceptions import CustomSchemasNotAvailableError, ExtractionSchemaNotFoundError
from app.repositories.schema_access_repository import SchemaAccessRepository
from app.services.schema_access_models import AvailableExtractionSchema


class SchemaAccessService:
    def __init__(self, repository: SchemaAccessRepository) -> None:
        self.repository = repository


    def list_available(self, *, user_id: UUID) -> list[AvailableExtractionSchema]:
        custom_schemas_enabled = self.repository.get_custom_schemas_enabled(user_id)

        if custom_schemas_enabled is None:
            raise LookupError("Utente non trovato.")

        rows = self.repository.list_available_versions(
            user_id=user_id,
            include_custom=custom_schemas_enabled,
        )

        return [
            AvailableExtractionSchema(
                schema_id=schema.id,
                schema_version_id=version.id,
                name=schema.name,
                domain=schema.domain,
                version=version.version,
                is_builtin=schema.is_builtin,
            )
            for schema, version in rows
        ]


    def assert_custom_schemas_enabled(self, *, user_id: UUID) -> None:
        custom_schemas_enabled = self.repository.get_custom_schemas_enabled(user_id)

        if custom_schemas_enabled is None:
            raise LookupError("Utente non trovato.")

        if not custom_schemas_enabled:
            raise CustomSchemasNotAvailableError("Gli schema personalizzati non sono disponibili per il piano corrente.")


    def authorize_for_analysis(
        self,
        *,
        user_id: UUID,
        requested_schema_version_id: UUID | None,
    ) -> UUID | None:
        if requested_schema_version_id is None:
            return None

        custom_schemas_enabled = self.repository.get_custom_schemas_enabled(user_id)

        if custom_schemas_enabled is None:
            raise LookupError("Utente non trovato.")

        row = self.repository.get_visible_version(
            user_id=user_id,
            schema_version_id=requested_schema_version_id,
        )

        if row is None:
            raise ExtractionSchemaNotFoundError("Schema di estrazione non trovato.")

        schema, version = row

        if not schema.is_builtin and not custom_schemas_enabled:
            raise CustomSchemasNotAvailableError(
                "Gli schema personalizzati non sono disponibili per il piano corrente."
            )

        return version.id