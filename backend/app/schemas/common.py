"""Define shared health-check and structured API-error response schemas."""

from typing import Any
from app.schemas.base import ApiModel


class HealthResponse(ApiModel):
    """Serialize the health data returned by the REST API."""

    status: str
    service: str
    version: str


class ErrorDetail(ApiModel):
    """Define the typed API contract for error detail."""

    code: str
    message: str
    details: list[dict[str, Any]] | None = None


class ErrorResponse(ApiModel):
    """Serialize the error data returned by the REST API."""

    error: ErrorDetail


class DatabaseHealthResponse(ApiModel):
    """Serialize the database health data returned by the REST API."""

    status: str
    database: str
    user: str
