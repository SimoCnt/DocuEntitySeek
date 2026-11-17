from fastapi import APIRouter

from app.api.routes import documents, health, admin, auth, analyses, schemas


api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(documents.router)
api_router.include_router(admin.router)
api_router.include_router(analyses.router, tags=["analyses"])
api_router.include_router(schemas.router)
