"""Query the active persisted AI runtime configuration."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AiRuntimeConfigModel


class AiRuntimeConfigRepository:
    """Read the active version of AI runtime configuration."""

    def __init__(self, session: Session) -> None:
        self.session = session


    def get_active(self) -> AiRuntimeConfigModel | None:
        """Load the currently active persisted AI runtime configuration."""

        statement = select(AiRuntimeConfigModel).where(AiRuntimeConfigModel.is_active.is_(True))
        
        return self.session.scalar(statement)
