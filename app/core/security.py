from datetime import datetime, timedelta, timezone

import jwt
from jwt import PyJWTError as JWTError
from passlib.context import CryptContext

from core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет соответствие пароля и хеша"""
    return pwd_context.verify(plain_password, hashed_password)


async def get_password_hash(password: str) -> str:
    """Создает хеш пароля"""
    return pwd_context.hash(password)


async def create_access_token(data: dict) -> str:
    """Создает access токен"""
    copy_data = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    copy_data.update({"exp": expire})
    encoded_jwt = jwt.encode(
        copy_data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def create_refresh_token(data: dict) -> str:
    """Создает refresh токен"""
    copy_data = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    copy_data.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        copy_data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def verify_token(token: str) -> dict | None:
    """Проверяет и декодирует JWT токен"""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None
