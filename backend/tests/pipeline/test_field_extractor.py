from uuid import uuid4
import pytest

from app.pipeline.config_models import FieldExtractionDefinition, ResolvedAiConfiguration, ResolvedExtractionSchema, RuntimeAiConfig
from app.pipeline.field_extractor import Gliner2FieldExtractor
from app.pipeline.model_provider import LoadedAiModel, ModelCacheKey
from app.pipeline.models import PreparedDocumentPage, PreparedDocumentText


class FakeFieldExtractor:
    def __init__(self) -> None:
        self.last_structures = None
        self.last_kwargs = None


    def extract_json_long(self, text, structures, **kwargs):
        self.last_structures = structures
        self.last_kwargs = kwargs

        value = "Comune di Palermo"
        start = text.index(value)

        return {
            "test_structure": [
                {
                    "ente_appaltante": {
                        "text": value,
                        "start": start,
                        "end": start + len(value),
                        "confidence": 0.93,
                    }
                }
            ]
        }


def make_field_config() -> ResolvedAiConfiguration:
    runtime = RuntimeAiConfig(
        id=uuid4(),
        name="Test",
        version=1,
        engine="GLINER2",
        model_id="test/model",
        model_revision=None,
        chunk_size=320,
        chunk_overlap=48,
        batch_size=4,
        num_workers=0,
        overlap_policy="allow",
        entity_threshold=0.5,
        field_threshold=0.67,
    )

    schema = ResolvedExtractionSchema(
        schema_id=uuid4(),
        schema_name="Test",
        schema_domain="TEST",
        structure_key="test_structure",
        version_id=uuid4(),
        version=1,
        entities=(),
        fields=(
            FieldExtractionDefinition(
                id=uuid4(),
                field_key="ente_appaltante",
                label="Ente appaltante",
                description="Ente che indice la procedura",
                data_type="str",
                is_required=False,
            ),
        ),
    )

    return ResolvedAiConfiguration(
        runtime=runtime,
        schema=schema,
        text_layout_version="page-join-v1",
    )


def make_document() -> PreparedDocumentText:
    text = "La stazione appaltante è il Comune di Palermo."

    return PreparedDocumentText(
        text=text,
        pages=(
            PreparedDocumentPage(
                page_number=1,
                text=text,
                global_start=0,
                global_end=len(text),
            ),
        ),
        layout_version="page-join-v1",
    )


def make_loaded_model(extractor) -> LoadedAiModel:
    return LoadedAiModel(
        cache_key=ModelCacheKey(
            engine="GLINER2",
            model_id="test/model",
            model_revision=None,
            device="cpu",
            quantize=False,
            compile=False,
        ),
        extractor=extractor,
    )


@pytest.mark.unit
def test_field_extractor_uses_dynamic_schema() -> None:
    fake = FakeFieldExtractor()

    result = Gliner2FieldExtractor().extract(
        document_id=uuid4(),
        document=make_document(),
        config=make_field_config(),
        model=make_loaded_model(fake),
    )

    assert fake.last_structures == {
        "test_structure": ["ente_appaltante::str::Ente che indice la procedura"]
    }

    assert fake.last_kwargs["threshold"] == 0.67
    assert fake.last_kwargs["chunk_size"] == 320
    assert fake.last_kwargs["chunk_overlap"] == 48
    assert fake.last_kwargs["batch_size"] == 4
    assert result.total_candidates == 1


@pytest.mark.unit
def test_field_candidate_preserves_global_span() -> None:
    result = Gliner2FieldExtractor().extract(
        document_id=uuid4(),
        document=make_document(),
        config=make_field_config(),
        model=make_loaded_model(FakeFieldExtractor()),
    )

    candidate = result.candidates[0]
    document = make_document()

    assert candidate.field_key == "ente_appaltante"
    assert document.text[candidate.start:candidate.end] == candidate.value
    assert candidate.confidence == pytest.approx(0.93)


class EmptyFieldExtractor:
    def extract_json_long(self, text, structures, **kwargs):
        return {"test_structure": [{}]}


@pytest.mark.unit
def test_missing_field_is_reported() -> None:
    result = Gliner2FieldExtractor().extract(
        document_id=uuid4(),
        document=make_document(),
        config=make_field_config(),
        model=make_loaded_model(EmptyFieldExtractor()),
    )

    assert result.total_candidates == 0
    assert result.missing_field_keys == ("ente_appaltante",)


from app.core.exceptions import AiInferenceError


class InvalidFieldSpanExtractor:
    def extract_json_long(self, text, structures, **kwargs):
        return {
            "test_structure": [
                {
                    "ente_appaltante": {
                        "text": "Comune di Palermo",
                        "start": 0,
                        "end": 18,
                        "confidence": 0.95,
                    }
                }
            ]
        }


@pytest.mark.unit
def test_invalid_field_span_is_rejected() -> None:
    with pytest.raises(AiInferenceError, match="non corrisponde"):
        Gliner2FieldExtractor().extract(
            document_id=uuid4(),
            document=make_document(),
            config=make_field_config(),
            model=make_loaded_model(InvalidFieldSpanExtractor()),
        )