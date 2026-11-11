from uuid import UUID
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import UserModel


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session


    def get_id_by_email(self, email: str) -> UUID | None:
        statement = (
            select(UserModel.id)
            .where(func.lower(UserModel.email) == email.lower())
            )
        
        return self.session.scalar(statement)