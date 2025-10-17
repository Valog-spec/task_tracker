from typing import List

from repositories.task_repository import TaskRepository
from schemas.task import TaskBaseSchema, TaskResponseSchema


class TaskService:
    """Сервис для работы с задачами"""

    def __init__(self, db_session) -> None:
        self.task_repository = TaskRepository(db_session=db_session)

    async def create_task(
        self, task_data: TaskBaseSchema, user_id: int
    ) -> TaskResponseSchema:
        """Создание задачи"""
        task_dict = task_data.model_dump()
        task_dict["user_id"] = user_id
        task = await self.task_repository.create_task(task_dict)
        return TaskResponseSchema.model_validate(task)

    async def get_user_tasks(self, user_id: int) -> List[TaskResponseSchema]:
        """Получение задач пользователя"""
        tasks = await self.task_repository.get_by_user_id(user_id)
        return [TaskResponseSchema.model_validate(task) for task in tasks]
