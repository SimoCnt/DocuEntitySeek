import pytest
from sqlalchemy.orm import Session

from app.pipeline.config_resolver import AiConfigurationResolver
from app.db.models import AiRuntimeConfigModel, FieldDefinitionModel, EntityDefinitionModel


@pytest.mark.integration
def test_resolve_active_ai_configuration(db_session: Session) -> None:
    resolver = AiConfigurationResolver(db_session)
    result = resolver.resolve()

    assert result.runtime.id is not None
    assert result.runtime.model_id
    assert result.runtime.engine
    assert result.runtime.chunk_size > 0
    assert result.runtime.chunk_overlap < result.runtime.chunk_size
    assert len(result.schema.entities) > 0
    assert len(result.schema.fields) > 0


@pytest.mark.integration
def test_runtime_model_id_comes_from_database(db_session: Session) -> None:
    config = (
        db_session.query(AiRuntimeConfigModel)
        .filter(AiRuntimeConfigModel.is_active.is_(True))
        .one()
    )

    config.model_id = "example/test-model"
    db_session.flush()

    result = AiConfigurationResolver(db_session).resolve()

    assert result.runtime.model_id == "example/test-model"


@pytest.mark.integration
def test_entity_definitions_come_from_database(db_session: Session) -> None:
    entity = db_session.query(EntityDefinitionModel).first()

    assert entity is not None

    entity.label = "ETICHETTA_TEST"
    db_session.flush()

    result = AiConfigurationResolver(db_session).resolve()
    labels = {definition.label for definition in result.schema.entities}

    assert "ETICHETTA_TEST" in labels


@pytest.mark.integration
def test_field_definitions_come_from_database(db_session: Session) -> None:
    field = db_session.query(FieldDefinitionModel).first()

    assert field is not None

    field.field_key = "campo_test"
    db_session.flush()

    result = AiConfigurationResolver(db_session).resolve()
    keys = {definition.field_key for definition in result.schema.fields}

    assert "campo_test" in keys


@pytest.mark.integration
def test_configuration_snapshot_is_json_serializable(db_session: Session) -> None:
    import json

    resolved = AiConfigurationResolver(db_session).resolve()
    snapshot = resolved.to_snapshot()
    serialized = json.dumps(snapshot)

    assert serialized
    assert snapshot["runtimeConfig"]["modelId"] == resolved.runtime.model_id