import pytest
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, EmailAlreadyRegisteredError
from app.services.auth_service import AuthService


@pytest.mark.integration
def test_register_creates_base_user(db_session: Session) -> None:
    service = AuthService(db_session)
    user = service.register(email="new@example.com", password="ValidPassword123!")

    assert user.id is not None
    assert user.email == "new@example.com"
    assert user.role == "USER"
    assert user.plan_code == "BASE"
    assert user.is_active is True
    assert user.password_hash is not None
    assert user.password_hash != "ValidPassword123!"


@pytest.mark.integration
def test_register_rejects_duplicate_email(db_session: Session) -> None:
    service = AuthService(db_session)
    service.register(email="duplicate@example.com", password="ValidPassword123!")

    with pytest.raises(EmailAlreadyRegisteredError):
        service.register(email="DUPLICATE@example.com", password="AnotherPassword123!")


@pytest.mark.integration
def test_authenticate_rejects_wrong_password(db_session: Session) -> None:
    service = AuthService(db_session)
    service.register(email="login@example.com", password="ValidPassword123!")

    with pytest.raises(AuthenticationError):
        service.authenticate(email="login@example.com", password="WrongPassword123!")


@pytest.mark.integration
def test_authenticate_updates_last_login(db_session: Session) -> None:
    service = AuthService(db_session)
    service.register(email="login@example.com", password="ValidPassword123!")

    user = service.authenticate(email="login@example.com", password="ValidPassword123!")

    assert user.last_login_at is not None