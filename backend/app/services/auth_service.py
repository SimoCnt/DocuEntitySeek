
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, EmailAlreadyRegisteredError
from app.core.security import hash_password, verify_and_update_password, verify_dummy_password
from app.db.models import UserModel
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.users = UserRepository(session)

    def register(self, *, email: str, password: str) -> UserModel:
        normalized_email = email.strip().lower()

        if self.users.get_by_email(normalized_email) is not None:
            raise EmailAlreadyRegisteredError("Esiste già un account associato a questa email.")

        user = self.users.create(email=normalized_email, password_hash=hash_password(password))
        user_id = user.id

        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise EmailAlreadyRegisteredError("Registrazione non riuscita per un conflitto sui dati.") from exc

        created_user = self.users.get_by_id(user_id)

        if created_user is None:
            raise RuntimeError("Impossibile recuperare l'utente appena creato.")

        return created_user

    def authenticate(self, *, email: str, password: str) -> UserModel:
        normalized_email = email.strip().lower()
        user = self.users.get_by_email(normalized_email)

        if user is None or not user.is_active or not user.password_hash:
            verify_dummy_password(password)
            raise AuthenticationError("Email o password non corretti.")

        valid, updated_hash = verify_and_update_password(password, user.password_hash)

        if not valid:
            raise AuthenticationError("Email o password non corretti.")

        if updated_hash:
            user.password_hash = updated_hash

        user.last_login_at = datetime.now(timezone.utc)
        self.session.commit()

        return user
