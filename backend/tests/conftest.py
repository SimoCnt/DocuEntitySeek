import os
from collections.abc import Callable, Generator
from uuid import UUID
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL, create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.security import create_access_token, hash_password
from app.db.models import UserModel
from app.db.session import get_db_session
from app.main import create_application


class TestEnvironment(BaseSettings):
    test_db_host: str = "localhost"
    test_db_port: int = 5432
    test_db_name: str = "docuentityseek_test"
    test_db_user: str = "docuentityseek_test_app"
    test_db_password: str
    test_jwt_secret_key: str

    model_config = SettingsConfigDict(
        env_file=".env.test", 
        env_file_encoding="utf-8", 
        extra="ignore"
        )


test_environment = TestEnvironment()

if test_environment.test_db_name != "docuentityseek_test":
    raise RuntimeError("I test possono essere eseguiti soltanto su 'docuentityseek_test'.")

os.environ["APP_ENV"] = "test"
os.environ["DEBUG"] = "false"
os.environ["DB_HOST"] = test_environment.test_db_host
os.environ["DB_PORT"] = str(test_environment.test_db_port)
os.environ["DB_NAME"] = test_environment.test_db_name
os.environ["DB_USER"] = test_environment.test_db_user
os.environ["DB_PASSWORD"] = test_environment.test_db_password
os.environ["JWT_SECRET_KEY"] = test_environment.test_jwt_secret_key

get_settings.cache_clear()


@pytest.fixture(scope="session")
def test_engine() -> Generator[Engine, None, None]:
    database_url = URL.create(
        drivername="postgresql+psycopg",
        username=test_environment.test_db_user,
        password=test_environment.test_db_password,
        host=test_environment.test_db_host,
        port=test_environment.test_db_port,
        database=test_environment.test_db_name,
    )

    engine = create_engine(database_url, pool_pre_ping=True)

    with engine.connect() as connection:
        database_name = connection.scalar(text("SELECT current_database()"))

        if database_name != "docuentityseek_test":
            raise RuntimeError(f"Connessione di test non sicura: database corrente = {database_name!r}.")

    yield engine
    engine.dispose()


@pytest.fixture
def db_session(test_engine: Engine) -> Generator[Session, None, None]:
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, expire_on_commit=False, join_transaction_mode="create_savepoint")

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def clean_api_database(test_engine: Engine) -> Generator[None, None, None]:
    def clean() -> None:
        with test_engine.begin() as connection:
            connection.execute(text("DELETE FROM users"))

    clean()
    yield
    clean()


@pytest.fixture
def app(test_engine: Engine, clean_api_database: None) -> Generator[FastAPI, None, None]:
    test_session_factory = sessionmaker(bind=test_engine, class_=Session, expire_on_commit=False)
    application = create_application()

    def override_db_session() -> Generator[Session, None, None]:
        session = test_session_factory()

        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    application.dependency_overrides[get_db_session] = override_db_session

    yield application
    application.dependency_overrides.clear()


@pytest.fixture
def client(app: FastAPI) -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def user_factory(db_session: Session) -> Callable[..., UserModel]:
    def create_user(
        *,
        email: str = "user@example.com",
        password: str = "ValidPassword123!",
        role: str = "USER",
        plan_code: str = "BASE",
        is_active: bool = True,
    ) -> UserModel:
        user = UserModel(
            email=email.lower(),
            password_hash=hash_password(password),
            role=role,
            plan_code=plan_code,
            is_active=is_active,
        )

        db_session.add(user)
        db_session.flush()

        return user

    return create_user


@pytest.fixture
def auth_headers() -> Callable[[UUID], dict[str, str]]:
    def create_headers(user_id: UUID) -> dict[str, str]:
        token = create_access_token(user_id)
        return {"Authorization": f"Bearer {token}"}

    return create_headers


@pytest.fixture
def api_db_session(test_engine: Engine, clean_api_database: None) -> Generator[Session, None, None]:
    session = Session(bind=test_engine, expire_on_commit=False)

    try:
        yield session
    finally:
        session.close()