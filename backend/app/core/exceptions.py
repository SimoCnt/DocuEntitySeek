"""Define domain-specific failures shared by API, storage, authentication, and AI layers."""

from uuid import UUID
from datetime import datetime


class DocumentNotFoundError(Exception):
    """Signal a document not found domain failure."""

    def __init__(self, document_id: str):
        self.document_id = (document_id)
        super().__init__(f"Documento '{document_id}' non trovato.")


class InvalidDocumentFileError(Exception):
    """Signal a invalid document file domain failure."""

    pass


class EmailAlreadyRegisteredError(Exception):
    """Signal a email already registered domain failure."""

    pass


class AuthenticationError(Exception):
    """Signal a authentication domain failure."""

    pass


class ForbiddenError(Exception):
    """Signal a forbidden domain failure."""

    pass


class DocumentStorageError(Exception):
    """Signal a document storage domain failure."""

    pass


class PdfTextExtractionError(Exception):
    """Signal a pdf text extraction domain failure."""

    pass


class AiConfigurationError(Exception):
    """Signal a ai configuration domain failure."""

    pass


class AiModelLoadError(Exception):
    """Signal a ai model load domain failure."""

    pass


class AiInferenceError(Exception):
    """Signal a ai inference domain failure."""

    pass


class SpanMappingError(Exception):
    """Signal a span mapping domain failure."""

    pass


class AnalysisExecutionError(Exception):
    """Signal a analysis execution domain failure."""

    def __init__(self, analysis_id: UUID) -> None:
        self.analysis_id = analysis_id

        super().__init__(f"Analisi {analysis_id} non completata.")


class AnalysisQuotaExceededError(Exception):
    """Signal a analysis quota exceeded domain failure."""

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
    """Signal a extraction schema not found domain failure."""

    pass


class CustomSchemasNotAvailableError(Exception):
    """Signal a custom schemas not available domain failure."""

    pass


class CustomSchemaNameConflictError(Exception):
    """Signal a custom schema name conflict domain failure."""

    pass


class CustomSchemaArchivedError(Exception):
    """Signal a custom schema archived domain failure."""

    pass
