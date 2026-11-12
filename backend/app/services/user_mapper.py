from app.db.models import UserModel
from app.schemas.auth import PlanCode, PlanResponse, UserResponse, UserRole


def to_user_response(user: UserModel) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        role=UserRole(user.role),
        plan=PlanResponse(
            code=PlanCode(user.plan.code),
            name=user.plan.name,
            daily_analysis_limit=user.plan.daily_analysis_limit,
            custom_schemas_enabled=user.plan.custom_schemas_enabled,
        ),
        is_active=user.is_active,
        created_at=user.created_at,
        last_login_at=user.last_login_at,
    )