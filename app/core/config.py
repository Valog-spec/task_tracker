from pathlib import Path
from typing import Optional

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = None
    REDIS_URL: Optional[str] = None

    # JWT настройки
    JWT_SECRET_KEY: str = "secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Redis настройки
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0

    # Database
    POSTGRES_HOST: str = "db_postgres"
    POSTGRES_USER: str = "myapp_user"
    POSTGRES_PASSWORD: str = "myapp_password"
    POSTGRES_DB: str = "myapp"
    POSTGRES_PORT: int = 5432

    @property
    def pg_connection_string(self):
        if self.DATABASE_URL:
            return self.DATABASE_URL.replace(
                "postgresql://", "postgresql+asyncpg://", 1
            )
        else:
            return (f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
                    f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}")


settings = Settings()
