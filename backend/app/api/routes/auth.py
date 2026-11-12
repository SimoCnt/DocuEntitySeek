from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import get_settings
from app.core.security import create_access_token
from app.dependencies import AuthServiceDep, CurrentUserDep
from app.schemas.auth import RegisterRequest, TokenResponse, UserResponse
from app.services.user_mapper import to_user_response


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
        "/register", 
        response_model=UserResponse, 
        status_code=status.HTTP_201_CREATED, 
        summary="Register user"
        )
def register(payload: RegisterRequest, service: AuthServiceDep) -> UserResponse:
    user = service.register(email=str(payload.email), password=payload.password)

    return to_user_response(user)


@router.post(
        "/token", 
        response_model=TokenResponse, 
        summary="Authenticate user"
        )
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], service: AuthServiceDep) -> TokenResponse:
    user = service.authenticate(email=form_data.username, password=form_data.password)
    settings = get_settings()
    token = create_access_token(user.id)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@router.get(
        "/me", 
        response_model=UserResponse, 
        summary="Get current user"
        )
def read_current_user(current_user: CurrentUserDep) -> UserResponse:
    return to_user_response(current_user)