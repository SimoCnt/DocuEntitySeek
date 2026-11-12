from fastapi import APIRouter

from app.dependencies import AdminUserDep, DbSessionDep
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserResponse
from app.services.user_mapper import to_user_response


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get(
        "/users", 
        response_model=list[UserResponse], 
        summary="List user metadata"
        )
def list_users(admin_user: AdminUserDep, session: DbSessionDep) -> list[UserResponse]:
    users = UserRepository(session).list_all()
    
    return [to_user_response(user) for user in users]