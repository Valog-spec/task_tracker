from fastapi import APIRouter, Depends

from core.dependencies import get_current_user
from schemas.user import UserResponseSchema

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponseSchema)
def get_me(current_user: UserResponseSchema = Depends(get_current_user)):
    """Получение информации о пользователе"""
    return current_user
