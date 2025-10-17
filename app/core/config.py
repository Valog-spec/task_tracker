from pathlib import Path
from typing import Optional

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # JWT настройки
    JWT_SECRET_KEY: str = "secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Redis настройки
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0

    # Database
    POSTGRES_HOST: str = "db_postgres"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "my_db"
    POSTGRES_PORT: int = 5432
    POOL_SIZE: int = 20

    model_config = ConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env", extra="ignore"
    )


settings = Settings()
