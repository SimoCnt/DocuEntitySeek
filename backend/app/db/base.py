"""Provide the shared SQLAlchemy declarative base for application tables."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base shared by every persisted SQLAlchemy model."""

    pass
