import gc
from dataclasses import dataclass, field
from threading import RLock
from time import perf_counter
from typing import Any, Protocol
import torch
from gliner2 import AutoExtractor

from app.core.exceptions import AiModelLoadError
from app.core.logging import get_logger
from app.pipeline.config_models import RuntimeAiConfig


logger = get_logger("pipeline.model")


def resolve_device(requested_device: str) -> str:
    normalized = requested_device.strip().lower()

    if normalized != "auto":
        return normalized

    if torch.cuda.is_available():
        return "cuda"

    mps = getattr(torch.backends, "mps", None)

    if mps is not None and mps.is_available():
        return "mps"

    return "cpu"



@dataclass(frozen=True, slots=True)
class AiExecutionEnvironment:
    device: str
    quantize: bool
    compile: bool


@dataclass(frozen=True, slots=True)
class ModelCacheKey:
    engine: str
    model_id: str
    model_revision: str | None
    device: str
    quantize: bool
    compile: bool


@dataclass(slots=True)
class LoadedAiModel:
    cache_key: ModelCacheKey
    extractor: Any
    inference_lock: Any = field(default_factory=RLock, repr=False, compare=False)


class AiModelLoader(Protocol):
    def load(
        self,
        *,
        runtime: RuntimeAiConfig,
        environment: AiExecutionEnvironment,
    ) -> Any:
        ...


class Gliner2ModelLoader:
    def load(self, *, runtime: RuntimeAiConfig, environment: AiExecutionEnvironment) -> Any:
        kwargs: dict[str, Any] = {
            "map_location": environment.device,
            "quantize": environment.quantize,
            "compile": environment.compile,
        }

        if runtime.model_revision:
            kwargs["revision"] = runtime.model_revision

        model = AutoExtractor.from_pretrained(runtime.model_id, **kwargs)
        model.eval()

        return model


class AiModelProvider:
    def __init__(
        self,
        *,
        loaders: dict[str, AiModelLoader],
        requested_device: str,
        quantize: bool,
        compile_model: bool,
    ) -> None:
        self.loaders = {key.upper(): value for key, value in loaders.items()}

        self.environment = AiExecutionEnvironment(
            device=resolve_device(requested_device),
            quantize=quantize,
            compile=compile_model,
        )

        self._cached: LoadedAiModel | None = None
        self._lock = RLock()


    def _build_cache_key(self, runtime: RuntimeAiConfig) -> ModelCacheKey:
        return ModelCacheKey(
            engine=runtime.engine.strip().upper(),
            model_id=runtime.model_id,
            model_revision=runtime.model_revision,
            device=self.environment.device,
            quantize=self.environment.quantize,
            compile=self.environment.compile,
        )


    def _load_model(
        self,
        *,
        loader: AiModelLoader,
        runtime: RuntimeAiConfig,
        cache_key: ModelCacheKey,
    ) -> LoadedAiModel:
        started_at = perf_counter()

        logger.info(
            "AI_MODEL | phase=load_start | engine=%s | model_id=%s | revision=%s | device=%s | quantize=%s | compile=%s",
            cache_key.engine,
            cache_key.model_id,
            cache_key.model_revision,
            cache_key.device,
            cache_key.quantize,
            cache_key.compile,
        )

        try:
            extractor = loader.load(runtime=runtime, environment=self.environment)

        except Exception as exc:
            logger.exception(
                "AI_MODEL | phase=load_failed | engine=%s | model_id=%s | revision=%s",
                cache_key.engine,
                cache_key.model_id,
                cache_key.model_revision,
            )

            raise AiModelLoadError("Impossibile caricare il modello AI configurato.") from exc

        loaded = LoadedAiModel(cache_key=cache_key, extractor=extractor)
        self._cached = loaded

        elapsed_ms = (perf_counter() - started_at) * 1000

        logger.info(
            "AI_MODEL | phase=load_complete | engine=%s | model_id=%s | revision=%s | device=%s | extractor_type=%s | elapsed_ms=%.2f",
            cache_key.engine,
            cache_key.model_id,
            cache_key.model_revision,
            cache_key.device,
            type(extractor).__name__,
            elapsed_ms,
        )

        return loaded


    def get_model(self, runtime: RuntimeAiConfig) -> LoadedAiModel:
        cache_key = self._build_cache_key(runtime)

        with self._lock:
            loader = self.loaders.get(cache_key.engine)

            if loader is None:
                raise AiModelLoadError(f"Motore AI non supportato: {cache_key.engine}")

            if self._cached is not None and self._cached.cache_key == cache_key:
                return self._cached

            self._release_cached_model()

            return self._load_model(
                loader=loader,
                runtime=runtime,
                cache_key=cache_key,
            )


    def _release_cached_model(self) -> None:
        if self._cached is None:
            return

        old_key = self._cached.cache_key

        logger.info(
            "AI_MODEL | phase=unload_start | model_id=%s | revision=%s",
            old_key.model_id,
            old_key.model_revision,
        )

        self._cached = None
        gc.collect()

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        logger.info(
            "AI_MODEL | phase=unload_complete | model_id=%s | revision=%s",
            old_key.model_id,
            old_key.model_revision,
        )


    def clear(self) -> None:
        with self._lock:
            self._release_cached_model()