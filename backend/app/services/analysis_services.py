from time import perf_counter
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.exceptions import DocumentNotFoundError
from app.core.exceptions import AnalysisExecutionError
from app.core.logging import get_logger
from app.domain.analysis import AnalysisStatus
from app.pipeline.analysis_pipeline import AnalysisPipeline
from app.pipeline.config_resolver import AiConfigurationResolver
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.document_repository import DocumentRepository
from app.services.analysis_models import AnalysisExecutionResult
from app.services.analysis_quota_service import AnalysisQuotaService
from app.services.analysis_quota_models import AnalysisQuotaDecision
from app.services.schema_access_service import SchemaAccessService


logger = get_logger("analysis")


class AnalysisService:
    def __init__(
        self,
        *,
        session: Session,
        config_resolver: AiConfigurationResolver,
        quota_service: AnalysisQuotaService,
        schema_access_service: SchemaAccessService,
        pipeline: AnalysisPipeline        
    ) -> None:
        self.session = session
        self.config_resolver = config_resolver
        self.quota_service = quota_service
        self.schema_access_service = schema_access_service
        self.pipeline = pipeline
        self.analyses = AnalysisRepository(session)
        self.documents = DocumentRepository(session)


    def run(
        self,
        *,
        document_id: UUID,
        owner_user_id: UUID,
        schema_version_id: UUID | None = None,
    ) -> AnalysisExecutionResult:
        started_at = perf_counter()

        logger.info(
            "ANALYSIS | phase=request | document_id=%s | requested_schema_version_id=%s",
            document_id,
            schema_version_id,
        )

        document = self.documents.get_by_id_and_owner(document_id=document_id, owner_user_id=owner_user_id)

        if document is None:
            raise DocumentNotFoundError(str(document_id))

        authorized_schema_version_id = self.schema_access_service.authorize_for_analysis(user_id=owner_user_id, requested_schema_version_id=schema_version_id)
        config = self.config_resolver.resolve(schema_version_id=authorized_schema_version_id, owner_user_id=owner_user_id)

        try:
            quota_decision = self.quota_service.assert_can_queue(user_id=owner_user_id)

            analysis = self.analyses.create_queued(
                document_id=document.id,
                schema_version_id=config.schema.version_id,
                ai_runtime_config_id=config.runtime.id,
                config=config.to_snapshot(),
            )

            analysis_id = analysis.id
            self.session.commit()

        except Exception:
            self.session.rollback()
            raise

        logger.info(
            "ANALYSIS | "
            "phase=queued | "
            "analysis_id=%s | "
            "document_id=%s | "
            "quota_limit=%s | "
            "quota_used_before=%d | "
            "quota_remaining_after=%s",
            analysis_id,
            document.id,
            quota_decision.daily_limit,
            quota_decision.used_or_reserved,
            quota_decision.remaining_after_queue,
        )

        try:
            return self._execute(
                analysis_id=analysis_id,
                document_id=document.id,
                owner_user_id=owner_user_id,
                config=config,
                quota_decision=quota_decision,
                started_at=started_at,
            )

        except Exception as exc:
            self._handle_failure(
                analysis_id=analysis_id,
                document_id=document.id,
                exc=exc,
            )

            raise AnalysisExecutionError(analysis_id) from exc


    def _execute(
        self,
        *,
        analysis_id: UUID,
        document_id: UUID,
        owner_user_id: UUID,
        config,
        quota_decision: AnalysisQuotaDecision,
        started_at: float,
    ) -> AnalysisExecutionResult:
        analysis = self.analyses.get_by_id(analysis_id)

        if analysis is None:
            raise RuntimeError("Analysis appena creata non trovata.")

        self.analyses.mark_processing(analysis)
        self.session.commit()

        logger.info(
            "ANALYSIS | phase=processing | analysis_id=%s | document_id=%s",
            analysis_id,
            document_id,
        )

        pipeline_result = self.pipeline.execute(
            analysis_id=analysis_id,
            document_id=document_id,
            owner_user_id=owner_user_id,
            config=config,
        )

        analysis = self.analyses.get_by_id(analysis_id)

        if analysis is None:
            raise RuntimeError("Analysis non trovata dopo la pipeline.")
        
        self.quota_service.consume_on_success(analysis=analysis, decision=quota_decision)
        self.analyses.mark_ready(analysis)
        self.session.commit()

        elapsed_ms = (perf_counter() - started_at) * 1000

        logger.info(
            "ANALYSIS | phase=ready | analysis_id=%s | document_id=%s | elapsed_ms=%.2f",
            analysis_id,
            document_id,
            elapsed_ms,
        )

        return AnalysisExecutionResult(
            analysis_id=analysis_id,
            status=AnalysisStatus.READY.value,
            pipeline=pipeline_result,
        )


    def _handle_failure(
        self,
        *,
        analysis_id: UUID,
        document_id: UUID,
        exc: Exception,
    ) -> None:
        self.session.rollback()

        logger.exception(
            "ANALYSIS | phase=failed | analysis_id=%s | document_id=%s | error_type=%s",
            analysis_id,
            document_id,
            type(exc).__name__,
        )

        try:
            analysis = self.analyses.get_by_id(analysis_id)

            if analysis is None:
                logger.error(
                    "ANALYSIS | phase=error_status_failed | analysis_id=%s | reason=analysis_not_found", analysis_id)
                return         

            self.analyses.mark_error(analysis, error_message=self._safe_error_message(exc))
            self.session.commit()

            logger.info(
                "ANALYSIS | phase=error_persisted | analysis_id=%s | document_id=%s",
                analysis_id,
                document_id,
            )

        except Exception:
            self.session.rollback()

            logger.exception(
                "ANALYSIS | phase=error_status_failed | analysis_id=%s | document_id=%s",
                analysis_id,
                document_id,
            )


    @staticmethod
    def _safe_error_message(exc: Exception) -> str:
        error_type = type(exc).__name__

        safe_messages = {
            "AiModelLoadError": "Caricamento del modello AI non riuscito.",
            "AiInferenceError": "Elaborazione AI non riuscita.",
            "SpanMappingError": "Mappatura della provenance non riuscita.",
            "PdfTextExtractionError": "Estrazione del testo PDF non riuscita.",
            "DocumentStorageError": "Accesso al documento non riuscito.",
        }

        return safe_messages.get(error_type, "Analisi non completata a causa di un errore interno.")