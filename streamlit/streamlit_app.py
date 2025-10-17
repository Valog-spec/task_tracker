import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8080")
st.set_page_config(page_title="JWT  Test")


def main() -> None:
    st.title("JWT аунтификация")

    page = st.sidebar.selectbox(
        "Выберите страницу", ["Регистрация", "Логин", "Профиль", "Выход"]
    )

    if page == "Регистрация":
        registration()
    elif page == "Логин":
        login()
    elif page == "Профиль":
        profile()
    elif page == "Выход":
        logout()


def registration() -> None:
    """Регистрация нового пользователя"""
    st.header("Регистрация")

    with st.form("registration_form"):
        email = st.text_input("Email")
        password = st.text_input("Пароль", type="password")
        submit = st.form_submit_button("Зарегистрироваться")

        if submit:
            if not email or not password:
                st.error("Заполните все поля")
                return

            try:
                response = requests.post(
                    f"{API_BASE_URL}/auth/register",
                    json={"email": email, "password": password},
                )

                if response.status_code == 201:
                    st.success("Регистрация прошла успешно! Теперь можете войти.")
                else:
                    error_msg = response.json().get("detail", "Ошибка регистрации")
                    st.error({error_msg})

            except requests.exceptions.RequestException as e:
                st.error(f"Ошибка подключения к API: {e}")


def login() -> None:
    """Аутефикация пользователя"""
    st.header("Вход в систему")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Пароль", type="password")
        submit = st.form_submit_button("Войти")

        if submit:
            if not email or not password:
                st.error("Заполните все поля")
                return

            try:
                response = requests.post(
                    f"{API_BASE_URL}/auth/login",
                    json={"email": email, "password": password},
                    headers={"Content-Type": "application/json"},
                )

                if response.status_code == 200:
                    data = response.json()
                    st.session_state.access_token = data["access_token"]
                    st.session_state.user_email = email

                    if response.cookies.get("refresh_token"):
                        st.session_state.refresh_token = response.cookies.get(
                            "refresh_token"
                        )

                    st.success(f"Вход успешен! Добро пожаловать, {email}")
                    st.json(data)
                else:
                    error_msg = response.json().get("detail", "Ошибка входа")
                    st.error({error_msg})

            except requests.exceptions.RequestException as e:
                st.error(f"Ошибка подключения к API: {e}")


def profile() -> None:
    """Получение профиля пользователя"""
    st.header("Профиль пользователя")

    if "access_token" not in st.session_state:
        st.warning("⚠Сначала войдите в систему")
        return

    if st.button("Обновить токены"):
        refresh_tokens()

    st.subheader("Текущая сессия")
    st.write(f"**Email:** {st.session_state.get('user_email', 'Неизвестно')}")
    st.write(f"**Access Token:** `{st.session_state.access_token}`")

    if st.button("📡 Получить данные профиля"):
        try:
            headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
            response = requests.get(f"{API_BASE_URL}/users/me", headers=headers)
            if response.status_code == 200:
                st.success("Данные получены успешно!")
                st.json(response.json())
            else:
                error_msg = response.json().get("detail", "Ошибка доступа")
                st.error(error_msg)

        except requests.exceptions.RequestException as e:
            st.error(f"Ошибка подключения к API: {e}")


def logout() -> None:
    """Выход из системы"""
    st.header("Выход из системы")

    if "access_token" not in st.session_state:
        st.info("Вы не авторизованы")
        return

    if st.button("Выйти"):
        try:
            headers = {"Authorization": f"Bearer {st.session_state.access_token}"}

            cookies = {}
            if "refresh_token" in st.session_state:
                cookies = {"refresh_token": st.session_state.refresh_token}

            response = requests.post(
                f"{API_BASE_URL}/auth/logout", headers=headers, cookies=cookies
            )

            if response.status_code == 200:
                for key in list(st.session_state.keys()):
                    del st.session_state[key]

                st.success("Выход выполнен успешно!")
            else:
                error_msg = response.json().get("detail", "Ошибка выхода")
                st.error(error_msg)

        except requests.exceptions.RequestException as e:
            st.error(f"Ошибка подключения к API: {e}")


def refresh_tokens() -> None:
    """Обновление access token через refresh token"""
    if "refresh_token" not in st.session_state:
        st.error("Refresh токен не найден")
        return

    try:
        cookies = {"refresh_token": st.session_state.refresh_token}
        response = requests.post(f"{API_BASE_URL}/auth/refresh", cookies=cookies)

        if response.status_code == 200:
            data = response.json()
            st.session_state.access_token = data["access_token"]
            if response.cookies.get("refresh_token"):
                st.session_state.refresh_token = response.cookies.get("refresh_token")
                st.success("Токены обновлены!")

        else:
            error_msg = response.json().get("detail", "Ошибка обновления")
            st.error(error_msg)

    except requests.exceptions.RequestException as e:
        st.error(f"Ошибка подключения к API: {e}")


if __name__ == "__main__":
    main()
    print(API_BASE_URL)
