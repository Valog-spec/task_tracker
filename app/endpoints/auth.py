from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials

from core.dependencies import get_auth_service, security
from schemas.user import (
    UserCreateSchema,
    UserLoginSchema,
    UserLogoutSchema,
    UserResponseSchema,
    UserTokenSchema,
)
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=UserResponseSchema,
    summary="Регистрация",
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserCreateSchema,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """Регистрация нового пользователя"""
    return await auth_service.register_user(user_data)


@router.post(
    "/login", summary="Аутентификация пользователя", response_model=UserTokenSchema
)
async def login(
    login_data: UserLoginSchema,
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """Аунтификация пользователя"""
    return await auth_service.authenticate_user(login_data, response)


@router.post("/refresh", summary="Обновление токенов", response_model=UserTokenSchema)
async def refresh_token(
    request: Request,
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """Обновление access и refresh токенов"""
    return await auth_service.refresh_tokens(request, response)


@router.post("/logout", summary="Выход из системы", response_model=UserLogoutSchema)
async def logout(
    request: Request,
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Выход пользователя из системы"""
    return await auth_service.logout(request, response, credentials)
