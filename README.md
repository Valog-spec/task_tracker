# Task Tracker API (Python + Streamlit)

## 📋 Описание проекта

Микросервисное приложение для управления задачами с авторизацией и веб-интерфейсом.

## 🛠 Технологии

### Бэкенд (FastAPI + PostgreSQL)
- **Регистрация и авторизация пользователей** (JWT)
- **Хеширование паролей** (bcrypt)
- **Операции для задач**:
  - Создание задач
  - Просмотр задач
- **Каждая задача привязана к дате и времени**
- **Аутентификация требуется для всех операций с задачами**

### Фронтенд (Streamlit)
- **Интерфейс регистрации**
- **Входа в систему**
- **Просмотр своего профиля(с обновлением токенов)**
- **Выход из системы**

## 🚀 Быстрый запуск

### Предварительные требования
- Установленный Docker и Docker Compose

### Запуск проекта

```bash

# Клонирование репозитория
git clone <repository-url>
cd task_tracker

# Сборка и запуск всех сервисов
docker-compose up --build

# Запуск в фоновом режиме
docker-compose up -d --build

# Остановка всех сервисов
docker-compose down
```
2. Создайте файл `.env` в директории `task_tracker/` со следующими параметрами по аналогии example.env:

```env
# JWT Settings
JWT_SECRET_KEY=secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis Settings
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# Database
POSTGRES_USER=myapp_user
POSTGRES_PASSWORD=myapp_password
POSTGRES_DB=myapp
POSTGRES_HOST=db_postgres
POSTGRES_PORT=5432

# Streamlit
API_BASE_URL = http://app:8080
```
## 🔧 API Endpoints

```
# Аутентификация
POST /register - Регистрация пользователя
POST /login - Вход в систему (получение JWT токена)
GET /users/me - Информация о текущем пользователе
# Задачи
GET /tasks/ - Получить все задачи пользователя
POST /tasks/ - Создать новую задачу
```

### Откройте браузер и перейдите по адресам:

* Streamlit интерфейс: http://localhost:8501
* API документация: http://localhost:8080/docs