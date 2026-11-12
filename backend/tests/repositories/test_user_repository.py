import pytest
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository


@pytest.mark.integration
def test_get_user_by_email_is_case_insensitive(db_session: Session, user_factory) -> None:
    user = user_factory(email="Simone@example.com")
    repository = UserRepository(db_session)
    found = repository.get_by_email("SIMONE@EXAMPLE.COM")

    assert found is not None
    assert found.id == user.id
    assert found.email == "simone@example.com"


@pytest.mark.integration
def test_missing_user_returns_none(db_session: Session) -> None:
    repository = UserRepository(db_session)
    found = repository.get_by_email("missing@example.com")

    assert found is None