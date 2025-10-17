from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import settings
from core.redis import redis_service
from core.security import verify_token
from services.auth_service import AuthService
from services.task_service import TaskService
from services.user_service import UserService

pg_connection_string = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
    f"{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)
# pg_connection_string = (
#     f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
#     f"localhost:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
# )
async_engine = create_async_engine(
    pg_connection_string,
    pool_pre_ping=True,
    pool_size=settings.POOL_SIZE,
)
async_session = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Создает и возвращает асинхронную сессию базы данных"""
    db = async_session()
    try:
        yield db
    finally:
        await db.close()


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """Получение текущего пользователя"""
    token = credentials.credentials
    auth_service = AuthService(db_session=db)
    if await auth_service.is_token_blacklisted(token):
        raise HTTPException(status_code=401, detail="Токен отозван")

    payload = await verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Не валиданый токен")

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Неверная структура токена")

    try:
        user_service = UserService(db_session=db)
        return await user_service.get_current_user(email)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


async def get_auth_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AuthService:
    """Создает и возращает сервис для работы с ауетификацией"""
    return AuthService(db_session=db)


async def get_user_service(db: Annotated[AsyncSession, Depends(get_db)]) -> UserService:
    """Создает и возращает сервис для работы с пользователем"""

    return UserService(db_session=db)


async def get_task_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskService:
    """Создает и возвращает сервис для работы с задачами"""
    return TaskService(db_session=db)


async def startup_event() -> None:
    """Инициализация подключения к Redis при запуске приложения"""
    await redis_service.init_redis()


async def shutdown_event() -> None:
    """Закрытие подключения к Redis при завершении работы приложения"""
    await redis_service.close()
