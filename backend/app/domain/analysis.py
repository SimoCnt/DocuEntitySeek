"""Define the persisted lifecycle states of a document analysis."""

from enum import Enum


class AnalysisStatus(str, Enum):
    """Persisted lifecycle states shared by API, services, and repositories."""

    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    READY = "READY"
    ERROR = "ERROR"
