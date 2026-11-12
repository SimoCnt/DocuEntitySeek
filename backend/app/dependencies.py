
from typing import Annotated
from uuid import UUID
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError, ForbiddenError
from app.core.security import decode_access_token, oauth2_scheme
from app.db.session import get_db_session
from app.db.models import UserModel
from app.repositories.user_repository import UserRepository
from app.services.document_service import DocumentService
from app.services.auth_service import AuthService


def get_document_service(session: DbSessionDep) -> DocumentService:
    return DocumentService(session)


def get_auth_service(session: DbSessionDep) -> AuthService:
    return AuthService(session)


def get_current_user(session: DbSessionDep, token: Annotated[str | None, Depends(oauth2_scheme)]) -> UserModel:
    if token is None:
        raise AuthenticationError("Autenticazione richiesta.")

    user_id = decode_access_token(token)
    user = UserRepository(session).get_by_id(user_id)

    if user is None:
        raise AuthenticationError("Utente associato al token non trovato.")

    if not user.is_active:
        raise ForbiddenError("Account disabilitato.")

    return user


def require_admin(current_user: CurrentUserDep) -> UserModel:
    if current_user.role != "ADMIN":
        raise ForbiddenError("Permessi amministrativi richiesti.")

    return current_user


DbSessionDep = Annotated[Session, Depends(get_db_session)]
DocumentServiceDep = Annotated[DocumentService, Depends(get_document_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
CurrentUserDep = Annotated[UserModel, Depends(get_current_user)]
AdminUserDep = Annotated[UserModel, Depends(require_admin)]
