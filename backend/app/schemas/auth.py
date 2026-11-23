from datetime import datetime
from enum import Enum
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator
from email_validator import EmailNotValidError, validate_email

from app.schemas.base import ApiModel


class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class PlanCode(str, Enum):
    BASE = "BASE"
    PREMIUM = "PREMIUM"


class RegisterRequest(ApiModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128, repr=False)

    @field_validator("email")
    @classmethod
    def validate_registration_email_domain(cls, value: str) -> str:
        try:
            validate_email(str(value), check_deliverability=True)
        except EmailNotValidError as exc:
            raise ValueError("Dominio email non valido o non abilitato a ricevere posta.") from exc
        return value


class PlanResponse(ApiModel):
    code: PlanCode
    name: str
    daily_analysis_limit: int | None
    custom_schemas_enabled: bool


class UserResponse(ApiModel):
    id: UUID
    email: EmailStr
    role: UserRole
    plan: PlanResponse
    is_active: bool
    created_at: datetime
    last_login_at: datetime | None


class AnalysisQuotaResponse(ApiModel):
    plan_code: PlanCode
    daily_limit: int | None
    used_or_reserved: int
    remaining: int | None
    resets_at: datetime
    is_unlimited: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int