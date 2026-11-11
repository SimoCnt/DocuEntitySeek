from collections.abc import Generator
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


settings = get_settings()

database_url = URL.create(
    drivername="postgresql+psycopg",
    username=settings.db_user,
    password=settings.db_password,
    host=settings.db_host,
    port=settings.db_port,
    database=settings.db_name,
)

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    echo=settings.sql_echo,
)

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    expire_on_commit=False,
)


def get_db_session() -> Generator[Session, None, None]:
    session = SessionLocal()

    try:
        yield session

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()