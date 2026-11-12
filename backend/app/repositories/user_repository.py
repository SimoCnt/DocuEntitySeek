from uuid import UUID
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.db.models import UserModel


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session


    
    def get_by_email(self, email: str) -> UserModel | None:
        statement = (
            select(UserModel)
            .where(func.lower(UserModel.email) == email.strip().lower())
            .options(joinedload(UserModel.plan))
        )

        return self.session.scalar(statement)



    def get_by_id(self, user_id: UUID) -> UserModel | None:
        statement = (
            select(UserModel)
            .where(UserModel.id == user_id)
            .options(joinedload(UserModel.plan))
        )

        return self.session.scalar(statement)
    

    def list_all(self) -> list[UserModel]:
        statement = (
            select(UserModel)
            .options(joinedload(UserModel.plan))
            .order_by(UserModel.created_at.desc())
        )

        return list(self.session.scalars(statement).all())


    def create(
        self,
        *,
        email: str,
        password_hash: str,
    ) -> UserModel:
        user = UserModel(
            email=email,
            password_hash=password_hash,
            role="USER",
            plan_code="BASE",
            is_active=True,
        )

        self.session.add(user)
        self.session.flush()

        return user