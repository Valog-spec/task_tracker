from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBaseSchema(BaseModel):
    """Базовая схема пользователя"""

    email: EmailStr


class UserCreateSchema(UserBaseSchema):
    """Схема для создания пользователя"""

    password: str


class UserResponseSchema(UserBaseSchema):
    """Схема ответа с данными пользователя"""

    id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class UserLoginSchema(BaseModel):
    """Схема для входа пользователя"""

    email: EmailStr
    password: str


class UserLogoutSchema(BaseModel):
    """Схема ответа при выходе"""

    message: str


class UserTokenSchema(BaseModel):
    """Схема с токенами пользователя"""

    access_token: str
    token_type: str
