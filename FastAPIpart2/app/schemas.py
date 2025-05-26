# app\schemas.py

from pydantic import BaseModel, Field, ConfigDict, field_validator, EmailStr
from typing import Optional
from datetime import datetime
from decimal import Decimal

# Импортируем Enum из models, чтобы использовать его в схемах
from .models import UserGroup

# --- Схемы для пользователя ---


class UserBase(BaseModel):
    """Базовая схема для пользователя."""

    username: str = Field(
        ..., min_length=3, max_length=50, description="Имя пользователя"
    )
    email: EmailStr = Field(
        ..., description="Адрес электронной почты"
    )  # Используем EmailStr для валидации email
    group: UserGroup = Field(
        default=UserGroup.USER, description="Группа пользователя (user или admin)"
    )


class UserCreate(UserBase):
    """Схема для создания нового пользователя."""

    password: str = Field(
        ..., min_length=6, description="Пароль пользователя (не менее 6 символов)"
    )


class UserUpdate(BaseModel):
    """Схема для обновления данных пользователя. Все поля опциональны."""

    username: Optional[str] = Field(
        None, min_length=3, max_length=50, description="Новое имя пользователя"
    )
    email: Optional[EmailStr] = Field(None, description="Новый адрес электронной почты")
    # Пароль обычно обновляется через отдельный эндпоинт, но можно добавить сюда
    # password: Optional[str] = Field(None, min_length=6, description="Новый пароль (не менее 6 символов)")
    group: Optional[UserGroup] = Field(
        None, description="Новая группа пользователя (только для админов)"
    )


class User(UserBase):
    """Схема для отображения данных пользователя (без пароля)."""

    id: int = Field(..., description="Уникальный идентификатор пользователя")
    created_at: datetime = Field(..., description="Дата и время создания")
    updated_at: datetime = Field(..., description="Дата и время последнего обновления")

    model_config = ConfigDict(from_attributes=True)


# --- Схемы для аутентификации ---


class UserLogin(BaseModel):
    """Схема для данных входа пользователя."""

    username: str = Field(..., description="Имя пользователя")
    password: str = Field(..., description="Пароль")


class Token(BaseModel):
    """Схема для JWT токена."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Схема для данных, закодированных в JWT токене."""

    username: Optional[str] = None
    # Можно добавить другие поля, например, user_id или group, если это нужно часто извлекать из токена
    # user_id: Optional[int] = None
    # group: Optional[UserGroup] = None


# --- Существующие схемы для Advertisement ---


class AdvertisementBase(BaseModel):
    title: str = Field(
        ..., min_length=1, max_length=100, description="Заголовок объявления"
    )
    description: Optional[str] = Field(
        None, max_length=500, description="Описание объявления"
    )
    price: Decimal = Field(
        ...,
        gt=0,
        max_digits=10,
        decimal_places=2,
        description="Цена объявления (должна быть больше 0)",
    )
    author: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Автор объявления (контактное лицо)",
    )


class AdvertisementCreate(AdvertisementBase):
    """Схема для данных, необходимых при создании нового объявления."""

    # owner_id будет устанавливаться автоматически на основе текущего пользователя
    pass


class AdvertisementUpdate(BaseModel):
    title: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Новый заголовок объявления"
    )
    description: Optional[str] = Field(
        None, max_length=500, description="Новое описание объявления"
    )
    price: Optional[Decimal] = Field(
        None,
        gt=0,
        max_digits=10,
        decimal_places=2,
        description="Новая цена объявления (должна быть больше 0)",
    )
    author: Optional[str] = Field(
        None, min_length=1, max_length=50, description="Новый автор объявления"
    )


class UserInAdvertisement(
    BaseModel
):  # Небольшая схема для отображения владельца в объявлении
    id: int
    username: str
    model_config = ConfigDict(from_attributes=True)


class Advertisement(AdvertisementBase):
    id: int = Field(..., description="Уникальный идентификатор объявления")
    created_at: datetime = Field(..., description="Дата и время создания")
    updated_at: datetime = Field(..., description="Дата и время последнего обновления")
    owner_id: int = Field(..., description="ID владельца объявления")
    owner: UserInAdvertisement = Field(..., description="Информация о владельце")

    model_config = ConfigDict(from_attributes=True)


class AdvertisementSearchParams(BaseModel):
    title: Optional[str] = Field(
        None, description="Часть заголовка для поиска (регистронезависимый)"
    )
    author: Optional[str] = Field(
        None, description="Точное имя автора для фильтрации (регистронезависимый)"
    )
    min_price: Optional[Decimal] = Field(None, ge=0, description="Минимальная цена")
    max_price: Optional[Decimal] = Field(None, gt=0, description="Максимальная цена")
    sort_by: Optional[str] = Field(
        "created_at",
        description="Поле для сортировки (например, 'created_at', 'price', 'title')",
    )
    order: Optional[str] = Field(
        "desc", description="Порядок сортировки ('asc' или 'desc')"
    )
    skip: int = Field(
        0, ge=0, description="Количество пропускаемых записей (для пагинации)"
    )
    limit: int = Field(
        10,
        ge=1,
        le=100,
        description="Максимальное количество записей на странице (для пагинации)",
    )

    # Валидаторы
    @field_validator("sort_by")
    def validate_sort_by(cls, value):
        allowed_fields = {"created_at", "price", "title", "author", "id", "updated_at"}
        if value not in allowed_fields:
            raise ValueError(
                f"Invalid sort field. Allowed fields: {', '.join(allowed_fields)}"
            )
        return value

    @field_validator("order")
    def validate_order(cls, value):
        allowed_orders = {"asc", "desc"}
        if value.lower() not in allowed_orders:
            raise ValueError("Invalid order value. Allowed values: 'asc', 'desc'")
        return value.lower()

    @field_validator("max_price")
    def validate_price_range(cls, max_price, values):
        min_price = values.data.get("min_price")
        if min_price is not None and max_price is not None and max_price < min_price:
            raise ValueError("max_price cannot be less than min_price")
        return max_price
