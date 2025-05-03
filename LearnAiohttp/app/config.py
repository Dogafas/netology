# app\config.py

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Определяем базовую директорию проекта
# BASE_DIR = Path(__file__).resolve().parent.parent # --> advertisement_app/app/
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # --> advertisement_app/

# Загружаем переменные окружения из файла .env в корне проекта
# Это полезно для локальной разработки, в Docker переменные будут установлены иначе
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"Loaded environment variables from: {env_path}")  # Для отладки
else:
    print(
        f".env file not found at: {env_path}, reading from system environment."
    )  # Для отладки

# --- Настройки Базы Данных (PostgreSQL) ---
POSTGRES_USER: Optional[str] = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD: Optional[str] = os.getenv("POSTGRES_PASSWORD")
# В Docker хостом будет имя сервиса 'db'. Для локального запуска можно оставить 'localhost'.
POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "db")
POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB: Optional[str] = os.getenv("POSTGRES_DB")

# Проверка наличия обязательных переменных для БД
if not all([POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB]):
    # В реальном приложении здесь лучше выбросить исключение или использовать
    # библиотеку для валидации настроек (например, Pydantic's BaseSettings)
    print(
        "Warning: One or more PostgreSQL environment variables "
        "(POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB) are not set."
    )
    # Для простоты примера, оставим None, но подключение упадет позже

# Формируем строку подключения (DSN) для SQLAlchemy asyncpg
# postgresql+asyncpg://user:password@host:port/database
DATABASE_URL: Optional[str] = None
if all([POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB]):
    DATABASE_URL = (
        f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
        f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    print(
        f"Database URL configured: postgresql+asyncpg://{POSTGRES_USER}:***@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
else:
    print("Warning: Database URL could not be constructed due to missing variables.")


# --- Настройки JWT ---
JWT_SECRET_KEY: Optional[str] = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
# Время жизни токена в минутах (по умолчанию 1 час)
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

if not JWT_SECRET_KEY:
    # В реальном приложении здесь нужно выбросить исключение
    print(
        "Warning: JWT_SECRET_KEY environment variable is not set. "
        "Authentication will not work correctly."
    )


# Выводим значения для проверки (кроме секретов)
print(f"JWT Algorithm: {JWT_ALGORITHM}")
print(f"Access Token Expire Minutes: {ACCESS_TOKEN_EXPIRE_MINUTES}")
