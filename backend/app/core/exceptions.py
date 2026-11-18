from uuid import UUID
from datetime import datetime


class DocumentNotFoundError(Exception):
    def __init__(self, document_id: str):
        self.document_id = (document_id)
        super().__init__(f"Documento '{document_id}' non trovato.")


class InvalidDocumentFileError(Exception):
    pass


class EmailAlreadyRegisteredError(Exception):
    pass


class AuthenticationError(Exception):
    pass


class ForbiddenError(Exception):
    pass


class DocumentStorageError(Exception):
    pass


class PdfTextExtractionError(Exception):
    pass


class AiConfigurationError(Exception):
    pass


class AiModelLoadError(Exception):
    pass


class AiInferenceError(Exception):
    pass


class SpanMappingError(Exception):
    pass


class AnalysisExecutionError(Exception):
    def __init__(self, analysis_id: UUID) -> None:
        self.analysis_id = analysis_id

        super().__init__(f"Analisi {analysis_id} non completata.")


class AnalysisQuotaExceededError(Exception):
    def __init__(
        self,
        *,
        daily_limit: int,
        used: int,
        resets_at: datetime,
    ) -> None:
        self.daily_limit = daily_limit
        self.used = used
        self.resets_at = resets_at

        super().__init__("Limite giornaliero di analisi raggiunto.")


class ExtractionSchemaNotFoundError(Exception):
    pass


class CustomSchemasNotAvailableError(Exception):
    pass


class CustomSchemaNameConflictError(Exception):
    pass


class CustomSchemaArchivedError(Exception):
    pass