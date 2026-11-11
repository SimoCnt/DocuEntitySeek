from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import get_settings
from app.schemas.common import HealthResponse, DatabaseHealthResponse
from app.dependencies import DbSessionDep


router = APIRouter(prefix="/health", tags=["health"])


@router.get(
        "",  
        response_model=HealthResponse, 
        summary="Check API health"
        )
async def health_check() -> HealthResponse:
    settings = get_settings()

    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version
    )



@router.get(
        "/database", 
        response_model=DatabaseHealthResponse, 
        summary="Check database health"
        )
def database_health_check(session: DbSessionDep) -> DatabaseHealthResponse:
    row = session.execute(
        text("""
            SELECT
                current_database() AS database,
                current_user AS username
        """)
    ).mappings().one()

    return DatabaseHealthResponse(
        status="ok",
        database=row["database"],
        user=row["username"],
    )
