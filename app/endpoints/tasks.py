from typing import List

from fastapi import APIRouter, Depends, status

from core.dependencies import get_current_user, get_task_service
from schemas.task import TaskBaseSchema, TaskResponseSchema
from schemas.user import UserResponseSchema
from services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post(
    "",
    response_model=TaskResponseSchema,
    summary="Создать задачу",
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    task_data: TaskBaseSchema,
    current_user: UserResponseSchema = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """Создание задачи пользователем"""
    return await task_service.create_task(task_data, current_user.id)


@router.get("", summary="Получить все задачи", response_model=List[TaskResponseSchema])
async def get_tasks(
    current_user: UserResponseSchema = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """Получение всез задач пользователя"""
    return await task_service.get_user_tasks(current_user.id)
