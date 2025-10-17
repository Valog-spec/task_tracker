from datetime import datetime, timezone

import jwt
from fastapi import HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials
from jwt import PyJWTError as JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.redis import get_redis
from core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from repositories.user_repository import UserRepository
from schemas.user import (
    UserCreateSchema,
    UserLoginSchema,
    UserLogoutSchema,
    UserResponseSchema,
    UserTokenSchema,
)


class AuthService:
    """Сервис для работы с аунтификацией"""

    def __init__(self, db_session: AsyncSession) -> None:
        self.user_repository = UserRepository(db_session=db_session)
        self.redis = None

    async def _get_redis(self):
        """Ленивая инициализация Redis клиента"""
        if self.redis is None:
            self.redis = await get_redis()
        return self.redis

    async def register_user(self, user_data: UserCreateSchema) -> UserResponseSchema:
        """Регистрация пользователя"""
        existing_user = await self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже зарегистрирован",
            )

        hashed_password = await get_password_hash(user_data.password)
        user_dict = user_data.model_dump()
        user_dict["password_hash"] = hashed_password
        del user_dict["password"]

        user = await self.user_repository.create_user(user_dict)
        return UserResponseSchema.model_validate(user)

    async def authenticate_user(
        self, login_data: UserLoginSchema, response: Response
    ) -> UserTokenSchema:
        """Аунтефикация пользователя"""
        user = await self.user_repository.get_by_email(login_data.email)
        if not user or not await verify_password(
            login_data.password, user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверные учетные данные",
            )

        access_token = await create_access_token(data={"sub": user.email})
        refresh_token = await create_refresh_token(data={"sub": user.email})

        await self._store_refresh_token(user.email, refresh_token)

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="lax",
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
            path="/auth/refresh",
        )
        return UserTokenSchema(access_token=access_token, token_type="bearer")

    async def refresh_tokens(self, request: Request, response: Response):
        """Обновление токенов"""
        redis = await self._get_redis()
        refresh_token = request.cookies.get("refresh_token")

        if not refresh_token:
            raise HTTPException(status_code=401, detail="Токен обновления отстуствует")

        if await redis.exists(f"blacklist:{refresh_token}"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен обновления отозван",
            )

        payload = await verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалидный токен"
            )

        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверная структура токена",
            )

        stored_token = await redis.get(f"refresh_token:{email}")
        if stored_token != refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токены обновления не совпадают",
            )

        new_access_token = await create_access_token(data={"sub": email})
        new_refresh_token = await create_refresh_token(data={"sub": email})

        await self._store_refresh_token(email, new_refresh_token)
        await self._add_to_blacklist(refresh_token, payload.get("exp"))

        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            samesite="lax",
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
            path="/auth/refresh",
        )

        return UserTokenSchema(access_token=new_access_token, token_type="bearer")

    async def logout(
        self,
        request: Request,
        response: Response,
        credentials: HTTPAuthorizationCredentials,
    ) -> UserLogoutSchema:
        """Выход из системы"""

        access_token = credentials.credentials
        refresh_token = request.cookies.get("refresh_token")

        await self._add_access_token_to_blacklist(access_token)

        if refresh_token:
            await self._add_refresh_token_to_blacklist(refresh_token)
            try:
                payload = await verify_token(refresh_token)
                if payload and payload.get("sub"):
                    redis_client = await get_redis()
                    await redis_client.delete(f"refresh_token:{payload.get('sub')}")
            except JWTError:
                pass

        response.delete_cookie(key="refresh_token", path="/auth/refresh")

        return UserLogoutSchema(message="Successfully logged out")

    async def is_token_blacklisted(self, token: str) -> bool:
        """Проверка токена в черном списке"""
        try:
            redis = await self._get_redis()
            key = f"blacklist:{token}"
            exists = await redis.exists(key)
            return exists
        except Exception:
            return False

    async def _store_refresh_token(self, email: str, refresh_token: str):
        """Сохраняет refresh token в Redis с TTL"""
        redis = await self._get_redis()
        expire_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600
        await redis.setex(f"refresh_token:{email}", expire_seconds, refresh_token)

    async def _add_to_blacklist(self, token: str, exp_timestamp: int):
        """Добавляет токен в черный список с TTL до истечения"""
        if exp_timestamp:
            current_time = datetime.now(timezone.utc).timestamp()
            ttl = max(1, int(exp_timestamp - current_time))
            redis_client = await get_redis()
            await redis_client.setex(f"blacklist:{token}", ttl, "revoked")

    async def _add_access_token_to_blacklist(self, token: str):
        """Добавляет access token в черный список"""
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            await self._add_to_blacklist(token, payload.get("exp"))
        except JWTError:
            pass

    async def _add_refresh_token_to_blacklist(self, token: str):
        """Добавляет refresh token в черный список"""
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            await self._add_to_blacklist(token, payload.get("exp"))
        except JWTError:
            pass
