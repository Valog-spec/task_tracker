from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TaskBaseSchema(BaseModel):
    """Базовая схема задачи"""

    title: str
    description: Optional[str] = None
    due_date: datetime


class TaskResponseSchema(TaskBaseSchema):
    """Схема ответа с данными задачи"""

    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
