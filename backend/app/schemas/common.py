from typing import Any
from app.schemas.base import ApiModel


class HealthResponse(ApiModel):
    status: str
    service: str
    version: str


class ErrorDetail(ApiModel):
    code: str
    message: str
    details: list[dict[str, Any]] | None = None


class ErrorResponse(ApiModel):
    error: ErrorDetail


class DatabaseHealthResponse(ApiModel):
    status: str
    database: str
    user: str