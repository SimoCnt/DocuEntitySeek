from uuid import uuid4
import pytest

from app.pipeline.config_models import EntityExtractionDefinition, ResolvedAiConfiguration, ResolvedExtractionSchema, RuntimeAiConfig
from app.pipeline.model_provider import LoadedAiModel, ModelCacheKey
from app.pipeline.models import PreparedDocumentPage, PreparedDocumentText
from app.pipeline.ner_extractor import Gliner2NerExtractor


class FakeExtractor:
    def __init__(self) -> None:
        self.last_entity_types = None
        self.last_kwargs = None


    def extract_entities_long(self, text, entity_types, **kwargs):
        self.last_entity_types = entity_types
        self.last_kwargs = kwargs

        entity_text = "Comune di Palermo"
        start = text.index(entity_text)

        return {
            "entities": {
                "ENTE_TEST": [
                    {
                        "text": entity_text,
                        "start": start,
                        "end": start + len(entity_text),
                        "confidence": 0.91,
                    }
                ]
            }
        }


def make_config() -> ResolvedAiConfiguration:
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
        entity_threshold=0.61,
        field_threshold=0.52,
    )

    schema = ResolvedExtractionSchema(
        schema_id=uuid4(),
        schema_name="Schema test",
        schema_domain="TEST",
        version_id=uuid4(),
        version=1,
        entities=(
            EntityExtractionDefinition(
                id=uuid4(),
                label="ENTE_TEST",
                description="Ente pubblico menzionato nel testo",
            ),
        ),
        fields=(),
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


def make_model(extractor) -> LoadedAiModel:
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
def test_ner_uses_dynamic_schema_and_runtime_config() -> None:
    fake = FakeExtractor()

    result = Gliner2NerExtractor().extract(
        document_id=uuid4(),
        document=make_document(),
        config=make_config(),
        model=make_model(fake),
    )

    assert fake.last_entity_types == {"ENTE_TEST": "Ente pubblico menzionato nel testo"}
    assert fake.last_kwargs["threshold"] == 0.61
    assert fake.last_kwargs["chunk_size"] == 320
    assert fake.last_kwargs["chunk_overlap"] == 48
    assert fake.last_kwargs["batch_size"] == 4
    assert fake.last_kwargs["overlap_policy"] == "allow"
    assert result.total_candidates == 1


@pytest.mark.unit
def test_ner_candidate_preserves_global_offsets() -> None:
    result = Gliner2NerExtractor().extract(
        document_id=uuid4(),
        document=make_document(),
        config=make_config(),
        model=make_model(FakeExtractor()),
    )

    candidate = result.candidates[0]
    document = make_document()

    assert document.text[candidate.start:candidate.end] == candidate.text
    assert candidate.label == "ENTE_TEST"
    assert candidate.confidence == pytest.approx(0.91)


from app.core.exceptions import AiInferenceError


class InvalidSpanExtractor:
    def extract_entities_long(self, text, entity_types, **kwargs):
        return {
            "entities": {
                "ENTE_TEST": [
                    {
                        "text": "Comune di Palermo",
                        "start": 0,
                        "end": 18,
                        "confidence": 0.95,
                    }
                ]
            }
        }


@pytest.mark.unit
def test_invalid_model_span_is_rejected() -> None:
    with pytest.raises(AiInferenceError, match="non corrisponde"):
        Gliner2NerExtractor().extract(
            document_id=uuid4(),
            document=make_document(),
            config=make_config(),
            model=make_model(InvalidSpanExtractor()),
        )