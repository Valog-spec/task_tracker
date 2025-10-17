from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.task import Task


class TaskRepository:
    """Репозиторий для работы с задачами"""

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def get_by_user_id(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Task]:
        """Получение всех задач пользователя"""
        result = await self.db_session.execute(
            select(Task).where(Task.user_id == user_id).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create_task(self, task_data: dict) -> Task:
        """Созаданик задачи"""
        db_task = Task(**task_data)
        self.db_session.add(db_task)
        await self.db_session.commit()
        await self.db_session.refresh(db_task)
        return db_task
