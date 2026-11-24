"""Persist and retrieve user accounts, including plan relationships."""

from uuid import UUID
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.db.models import UserModel


class UserRepository:
    """Manage persisted user records and their plan relationships."""

    def __init__(self, session: Session) -> None:
        self.session = session


    
    def get_by_email(self, email: str) -> UserModel | None:
        """Retrieve an account by normalized email address."""

        statement = (
            select(UserModel)
            .where(func.lower(UserModel.email) == email.strip().lower())
            .options(joinedload(UserModel.plan))
        )

        return self.session.scalar(statement)



    def get_by_id(self, user_id: UUID) -> UserModel | None:
        """Retrieve an account and plan metadata by account ID."""

        statement = (
            select(UserModel)
            .where(UserModel.id == user_id)
            .options(joinedload(UserModel.plan))
        )

        return self.session.scalar(statement)
    

    def list_all(self) -> list[UserModel]:
        """Load all accounts for administrator-only listing."""

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
        """Persist a new Base-plan account with a hashed password."""

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
