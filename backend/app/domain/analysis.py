from enum import Enum


class AnalysisStatus(str, Enum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    READY = "READY"
    ERROR = "ERROR"