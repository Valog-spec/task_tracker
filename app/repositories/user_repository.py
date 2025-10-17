from typing import Optional

from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User


class UserRepository:
    """Репозиторий для работы с пользователем"""

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def get_by_email(self, email: EmailStr) -> Optional[User]:
        """Получение пользователя по email"""
        result = await self.db_session.execute(select(User).filter(User.email == email))
        return result.scalar()

    async def create_user(self, user_data: dict) -> User:
        """Создание нового пользователя"""
        db_user = User(**user_data)
        self.db_session.add(db_user)
        await self.db_session.commit()
        await self.db_session.refresh(db_user)
        return db_user
