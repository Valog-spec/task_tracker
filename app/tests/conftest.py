import asyncio
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.dependencies import get_db
from main import create_application
from models.base import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///./tests/test.db"

engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)

AsyncTestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Создает event loop для тестовой сессии."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function", autouse=True)
async def setup_db():
    """Создает и удаляет таблицы для каждого теста."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Создает сессию БД для каждого теста."""
    async with AsyncTestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Создает асинхронного тестового клиента."""

    app = create_application()

    async def override_get_db():
        try:
            yield db_session
        finally:
            await db_session.close()

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://localhost"
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Данные для тестового пользователя"""
    return {"email": "test@example.com", "password": "testpassword123"}


@pytest.fixture
def another_user_data():
    """Данные другого тестового пользователя"""
    return {"email": "another@example.com", "password": "anotherpassword123"}
