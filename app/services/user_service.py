from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.user_repository import UserRepository
from schemas.user import UserResponseSchema


class UserService:
    """Сервис для работы с пользователем"""

    def __init__(self, db_session: AsyncSession) -> None:
        self.user_repository = UserRepository(db_session=db_session)

    async def get_current_user(self, email: str) -> UserResponseSchema:
        """Получение текущего пользователя"""
        user = await self.user_repository.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
            )
        return UserResponseSchema.model_validate(user)
