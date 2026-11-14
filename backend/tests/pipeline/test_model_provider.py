from typing import Any
from uuid import uuid4

import pytest

from app.core.exceptions import AiModelLoadError
from app.pipeline.config_models import RuntimeAiConfig
from app.pipeline.model_provider import AiExecutionEnvironment, AiModelProvider


class FakeModel:
    def __init__(self, model_id: str) -> None:
        self.model_id = model_id


class FakeLoader:
    def __init__(self) -> None:
        self.calls = 0


    def load(self, *, runtime: RuntimeAiConfig, environment: AiExecutionEnvironment) -> Any:
        self.calls += 1

        return FakeModel(runtime.model_id)


def make_runtime(
    *,
    model_id: str = "test/model-a",
    model_revision: str | None = None,
    engine: str = "GLINER2",
    entity_threshold: float = 0.5,
) -> RuntimeAiConfig:
    return RuntimeAiConfig(
        id=uuid4(),
        name="Test",
        version=1,
        engine=engine,
        model_id=model_id,
        model_revision=model_revision,
        chunk_size=512,
        chunk_overlap=96,
        entity_threshold=entity_threshold,
        field_threshold=0.5,
    )


@pytest.mark.unit
def test_provider_loads_model() -> None:
    loader = FakeLoader()

    provider = AiModelProvider(
        loaders={"GLINER2": loader},
        requested_device="cpu",
        quantize=False,
        compile_model=False,
    )

    loaded = provider.get_model(make_runtime())

    assert loader.calls == 1
    assert loaded.extractor.model_id == "test/model-a"


@pytest.mark.unit
def test_provider_reuses_cached_model() -> None:
    loader = FakeLoader()

    provider = AiModelProvider(
        loaders={"GLINER2": loader},
        requested_device="cpu",
        quantize=False,
        compile_model=False,
    )

    runtime = make_runtime()
    first = provider.get_model(runtime)
    second = provider.get_model(runtime)

    assert loader.calls == 1
    assert first is second


@pytest.mark.unit
def test_provider_reloads_when_model_changes() -> None:
    loader = FakeLoader()

    provider = AiModelProvider(
        loaders={"GLINER2": loader},
        requested_device="cpu",
        quantize=False,
        compile_model=False,
    )

    first = provider.get_model(make_runtime(model_id="test/model-a"))
    second = provider.get_model(make_runtime(model_id="test/model-b"))

    assert loader.calls == 2
    assert first is not second
    assert second.extractor.model_id == "test/model-b"


@pytest.mark.unit
def test_provider_reloads_when_revision_changes() -> None:
    loader = FakeLoader()

    provider = AiModelProvider(
        loaders={"GLINER2": loader},
        requested_device="cpu",
        quantize=False,
        compile_model=False,
    )

    provider.get_model(make_runtime(model_revision="revision-a"))
    provider.get_model(make_runtime(model_revision="revision-b"))

    assert loader.calls == 2


@pytest.mark.unit
def test_threshold_change_does_not_reload_model() -> None:
    loader = FakeLoader()

    provider = AiModelProvider(
        loaders={"GLINER2": loader},
        requested_device="cpu",
        quantize=False,
        compile_model=False,
    )

    first = provider.get_model(make_runtime(entity_threshold=0.5))
    second = provider.get_model(make_runtime(entity_threshold=0.8))

    assert loader.calls == 1
    assert first is second


@pytest.mark.unit
def test_unsupported_engine_is_rejected() -> None:
    provider = AiModelProvider(
        loaders={},
        requested_device="cpu",
        quantize=False,
        compile_model=False,
    )

    with pytest.raises(AiModelLoadError, match="non supportato"):
        provider.get_model(make_runtime(engine="UNKNOWN"))