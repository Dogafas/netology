# app\schemas\user.py
import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# --- Базовые схемы ---


class UserBase(BaseModel):
    """Базовая схема для пользователя, содержит общие поля."""

    email: EmailStr  # Pydantic автоматически валидирует формат email


class UserCreate(UserBase):
    """Схема для создания нового пользователя."""

    # Пароль нужен при создании, задаем минимальную/максимальную длину
    password: str = Field(
        ..., min_length=6, max_length=128
    )  # ... означает обязательное поле


# --- Схемы для запросов ---


class UserLogin(BaseModel):
    """Схема для входа пользователя."""

    email: EmailStr
    password: str


# --- Схемы для ответов ---


class UserResponse(UserBase):
    """Схема для ответа API, возвращающая информацию о пользователе."""

    id: int
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
