# app\schemas\advertisement.py

import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

# --- Базовые схемы ---


class AdvertisementBase(BaseModel):
    """Базовая схема для объявления."""

    title: str = Field(
        ..., min_length=1, max_length=100
    )  # Обязательный заголовок с ограничением длины
    description: Optional[str] = None  # Описание не обязательно


class AdvertisementCreate(AdvertisementBase):
    """Схема для создания нового объявления."""

    # При создании поля из базовой схемы уже включены
    pass  # Пока нет дополнительных полей, специфичных для создания


class AdvertisementUpdate(BaseModel):
    """
    Схема для обновления существующего объявления.
    Все поля опциональны, так как пользователь может захотеть обновить только часть данных.
    """

    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


# --- Схемы для ответов ---


class AdvertisementResponse(AdvertisementBase):
    """Схема для ответа API, возвращающая информацию об объявлении."""

    id: int
    created_at: datetime.datetime
    owner_id: int
    # Можно добавить информацию о владельце, если это необходимо
    # owner: UserResponse # Если раскомментировать, Pydantic попытается получить связанный объект owner
    model_config = ConfigDict(from_attributes=True)
