import redis.asyncio as redis

from core.config import settings


class RedisService:
    """Сервис для работы с Redis"""

    def __init__(self):
        self.redis_client = None

    async def init_redis(self) -> None:
        """Инициализация подключения к Redis"""
        if settings.REDIS_URL:
            # Render дает REDIS_URL в формате redis:// или rediss://
            self.redis_client = redis.Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
        else:
            # Локальная разработка
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                decode_responses=True,
            )
        await self.redis_client.ping()  # тестовое подключение

    async def close(self) -> None:
        """Закрытие подключения к Redis"""
        if self.redis_client:
            await self.redis_client.close()

    async def setex(self, key: str, time: int, value: str) -> None:
        """Установка значения с TTL"""
        await self.redis_client.setex(key, time, value)

    async def get(self, key: str) -> str | None:
        """Получение значения по ключу"""
        return await self.redis_client.get(key)

    async def exists(self, key: str) -> bool:
        """Проверка существования ключа"""
        return await self.redis_client.exists(key)

    async def delete(self, key: str) -> None:
        """Удаление ключа"""
        await self.redis_client.delete(key)


redis_service = RedisService()


async def get_redis() -> RedisService:
    """Получение экземпляра Redis сервиса"""
    if not redis_service.redis_client:
        await redis_service.init_redis()
    return redis_service
