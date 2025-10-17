from typing import Dict

from fastapi import status
from httpx import AsyncClient


class TestAuthRegistration:
    """Тесты регистрации пользователя"""

    async def test_register_success(self, client: AsyncClient, test_user_data: Dict):
        """Успешная регистрация пользователя"""
        response = await client.post("/auth/register", json=test_user_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "id" in data

    async def test_register_exists_email(
        self, client: AsyncClient, test_user_data: Dict
    ):
        """Регистрация с существующим email"""

        await client.post("/auth/register", json=test_user_data)

        response = await client.post("/auth/register", json=test_user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "уже зарегистрирован" in response.json()["detail"].lower()

    async def test_register_invalid_email(self, client: AsyncClient):
        """Регистрация с невалидным email"""
        invalid_data = {"email": "invalid-email", "password": "password"}
        response = await client.post("/auth/register", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
