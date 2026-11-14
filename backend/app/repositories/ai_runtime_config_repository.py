from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AiRuntimeConfigModel


class AiRuntimeConfigRepository:
    def __init__(self, session: Session) -> None:
        self.session = session


    def get_active(self) -> AiRuntimeConfigModel | None:
        statement = select(AiRuntimeConfigModel).where(AiRuntimeConfigModel.is_active.is_(True))
        
        return self.session.scalar(statement)