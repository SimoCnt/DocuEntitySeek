
from typing import Annotated
from uuid import UUID
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db_session
from app.repositories.user_repository import UserRepository
from app.services.document_service import DocumentService


DbSessionDep = Annotated[Session, Depends(get_db_session)]


def get_document_service(session: DbSessionDep) -> DocumentService:
    return DocumentService(session)


DocumentServiceDep = Annotated[DocumentService, Depends(get_document_service)]


def get_development_user_id(session: DbSessionDep) -> UUID:
    settings = get_settings()
    repository = UserRepository(session)
    user_id = repository.get_id_by_email(settings.development_user_email)

    if user_id is None:
        raise RuntimeError("Development user not found. Execute 02_seed.sql first.")

    return user_id


DevelopmentUserIdDep = Annotated[UUID, Depends(get_development_user_id)]
