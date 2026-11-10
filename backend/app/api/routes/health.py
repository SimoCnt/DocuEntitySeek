from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.common import HealthResponse


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