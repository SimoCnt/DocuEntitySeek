from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from app.core.exceptions import CustomSchemasNotAvailableError, CustomSchemaNameConflictError, ExtractionSchemaNotFoundError
from app.dependencies import CurrentUserDep, CustomSchemaServiceDep, SchemaAccessServiceDep
from app.schemas.custom_schema import CustomEntityDefinitionResponse, CustomFieldDefinitionResponse, CustomSchemaCreateRequest, CustomSchemaResponse, CustomSchemaSummaryResponse, CustomSchemaUpdateRequest
from app.schemas.extraction_schema import AvailableExtractionSchemaResponse
from app.services.custom_schema_models import CustomEntityDefinitionInput, CustomFieldDefinitionInput, CustomSchemaCreateCommand


router = APIRouter(
    prefix="/schemas",
    tags=["schemas"],
)


def _custom_schema_response(result) -> CustomSchemaResponse:
    return CustomSchemaResponse(
        schema_id=result.schema_id,
        schema_version_id=result.schema_version_id,
        name=result.name,
        domain=result.domain,
        version=result.version,
        created_at=result.created_at,
        entities=[
            CustomEntityDefinitionResponse(
                id=entity.id,
                label=entity.label,
                description=entity.description,
                color=entity.color,
                sort_order=entity.sort_order,
            )
            for entity in result.entities
        ],
        fields=[
            CustomFieldDefinitionResponse(
                id=field.id,
                field_key=field.field_key,
                label=field.label,
                description=field.description,
                data_type=field.data_type,
                is_required=field.is_required,
                sort_order=field.sort_order,
            )
            for field in result.fields
        ],
    )


@router.get("/available", response_model=list[AvailableExtractionSchemaResponse])
def list_available_schemas(current_user: CurrentUserDep, service: SchemaAccessServiceDep) -> list[AvailableExtractionSchemaResponse]:
    schemas = service.list_available(user_id=current_user.id)

    return [
        AvailableExtractionSchemaResponse(
            schema_id=schema.schema_id,
            schema_version_id=schema.schema_version_id,
            name=schema.name,
            domain=schema.domain,
            version=schema.version,
            is_builtin=schema.is_builtin,
        )
        for schema in schemas
    ]


@router.post(
    "/custom",
    response_model=CustomSchemaResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_custom_schema(
    payload: CustomSchemaCreateRequest,
    current_user: CurrentUserDep,
    service: CustomSchemaServiceDep,
) -> CustomSchemaResponse:
    try:
        result = service.create(
            user_id=current_user.id,
            command=CustomSchemaCreateCommand(
                name=payload.name,
                domain=payload.domain,
                entities=tuple(
                    CustomEntityDefinitionInput(
                        label=entity.label,
                        description=entity.description,
                    )
                    for entity in payload.entities
                ),
                fields=tuple(
                    CustomFieldDefinitionInput(
                        field_key=field.field_key,
                        label=field.label,
                        description=field.description,
                        is_required=field.is_required,
                    )
                    for field in payload.fields
                ),
            ),
        )

    except CustomSchemaNameConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "CUSTOM_SCHEMA_NAME_CONFLICT",
                "message": "Esiste già uno schema personalizzato con questo nome.",
            },
        ) from exc

    except CustomSchemasNotAvailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "CUSTOM_SCHEMAS_NOT_AVAILABLE",
                "message": "Gli schema personalizzati non sono disponibili per il piano corrente.",
            },
        ) from exc

    return _custom_schema_response(result)


@router.get(
    "/custom",
    response_model=list[CustomSchemaSummaryResponse],
)
def list_custom_schemas(
    current_user: CurrentUserDep,
    service: CustomSchemaServiceDep,
) -> list[CustomSchemaSummaryResponse]:
    try:
        schemas = service.list_owned(user_id=current_user.id)

    except CustomSchemasNotAvailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "CUSTOM_SCHEMAS_NOT_AVAILABLE",
                "message": "Gli schema personalizzati non sono disponibili per il piano corrente.",
            },
        ) from exc

    return [
        CustomSchemaSummaryResponse(
            schema_id=schema.schema_id,
            schema_version_id=schema.schema_version_id,
            name=schema.name,
            domain=schema.domain,
            version=schema.version,
            entity_count=schema.entity_count,
            field_count=schema.field_count,
            created_at=schema.created_at,
        )
        for schema in schemas
    ]


@router.get("/custom/{schema_id}", response_model=CustomSchemaResponse)
def get_custom_schema(
    schema_id: UUID,
    current_user: CurrentUserDep,
    service: CustomSchemaServiceDep,
) -> CustomSchemaResponse:
    try:
        result = service.get_owned(user_id=current_user.id, schema_id=schema_id)

    except ExtractionSchemaNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "EXTRACTION_SCHEMA_NOT_FOUND",
                "message": "Schema di estrazione non trovato.",
            },
        ) from exc

    except CustomSchemasNotAvailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "CUSTOM_SCHEMAS_NOT_AVAILABLE",
                "message": "Gli schema personalizzati non sono disponibili per il piano corrente.",
            },
        ) from exc

    return _custom_schema_response(result)


@router.put("/custom/{schema_id}", response_model=CustomSchemaResponse)
def update_custom_schema(
    schema_id: UUID,
    payload: CustomSchemaUpdateRequest,
    current_user: CurrentUserDep,
    service: CustomSchemaServiceDep,
) -> CustomSchemaResponse:
    try:
        result = service.update(
            user_id=current_user.id,
            schema_id=schema_id,
            command=CustomSchemaCreateCommand(
                name=payload.name,
                domain=payload.domain,
                entities=tuple(
                    CustomEntityDefinitionInput(
                        label=entity.label,
                        description=entity.description,
                    )
                    for entity in payload.entities
                ),
                fields=tuple(
                    CustomFieldDefinitionInput(
                        field_key=field.field_key,
                        label=field.label,
                        description=field.description,
                        is_required=field.is_required,
                    )
                    for field in payload.fields
                ),
            ),
        )

    except ExtractionSchemaNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "EXTRACTION_SCHEMA_NOT_FOUND",
                "message": "Schema di estrazione non trovato.",
            },
        ) from exc

    except CustomSchemaNameConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "CUSTOM_SCHEMA_NAME_CONFLICT",
                "message": "Esiste già uno schema personalizzato con questo nome.",
            },
        ) from exc

    except CustomSchemasNotAvailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "CUSTOM_SCHEMAS_NOT_AVAILABLE",
                "message": "Gli schema personalizzati non sono disponibili per il piano corrente.",
            },
        ) from exc

    return _custom_schema_response(result)