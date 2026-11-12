from datetime import datetime, timedelta, timezone
from uuid import UUID
import jwt
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError


settings = get_settings()
password_hash = PasswordHash.recommended()
dummy_hash = password_hash.hash("docuentityseek-dummy-password-not-used")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/token", auto_error=False)


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_dummy_password(password: str) -> None:
    password_hash.verify(password, dummy_hash)


def verify_and_update_password(password: str, encoded_hash: str) -> tuple[bool, str | None]:
    return password_hash.verify_and_update(password, encoded_hash)


def create_access_token(user_id: UUID) -> str:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)

    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": now,
        "exp": expires_at,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
    }

    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> UUID:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
            options={"require": ["sub", "type", "iat", "exp", "iss", "aud"]},
        )

        if payload.get("type") != "access":
            raise AuthenticationError("Token di autenticazione non valido.")

        return UUID(str(payload["sub"]))

    except (InvalidTokenError, KeyError, TypeError, ValueError) as exc:
        raise AuthenticationError("Token di autenticazione non valido o scaduto.") from exc