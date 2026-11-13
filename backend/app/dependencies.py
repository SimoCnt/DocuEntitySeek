
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, ForbiddenError
from app.core.security import decode_access_token, oauth2_scheme
from app.db.session import get_db_session
from app.db.models import UserModel
from app.repositories.user_repository import UserRepository
from app.services.document_service import DocumentService
from app.services.auth_service import AuthService


# 1. Dipendenza per la sessione del database
DbSessionDep = Annotated[Session, Depends(get_db_session)]


# 2. Servizi applicativi
def get_document_service(session: DbSessionDep) -> DocumentService:
    return DocumentService(session)


def get_auth_service(session: DbSessionDep) -> AuthService:
    return AuthService(session)


# 3. Autenticazione dell'utente corrente
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


# 4. Dipendenza dell'utente autenticato
CurrentUserDep = Annotated[UserModel, Depends(get_current_user)]


# 5. Autorizzazione amministratore
def require_admin(current_user: CurrentUserDep) -> UserModel:
    if current_user.role != "ADMIN":
        raise ForbiddenError("Permessi amministrativi richiesti.")

    return current_user


# 6. Altre dipendenze utilizzabili nelle rotte
DocumentServiceDep = Annotated[DocumentService, Depends(get_document_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
AdminUserDep = Annotated[UserModel, Depends(require_admin)]
