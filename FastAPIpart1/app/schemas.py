from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator,
)
from typing import Optional
from datetime import datetime
from decimal import Decimal  # Используем Decimal для точности цены


# --- Базовая схема для объявления ---
class AdvertisementBase(BaseModel):
    """
    Базовая схема Pydantic для объявления.
    Содержит поля, общие для создания и чтения.
    """

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
        ..., min_length=1, max_length=50, description="Автор объявления"
    )

    # Пример валидатора на уровне модели, если бы он был нужен
    # @field_validator('title')
    # def title_must_not_contain_spam(cls, value):
    #     if "spam" in value.lower():
    #         raise ValueError("Title cannot contain spam")
    #     return value


# --- Схема для создания объявления ---
class AdvertisementCreate(AdvertisementBase):
    """
    Схема для данных, необходимых при создании нового объявления.
    Наследует все поля от AdvertisementBase.
    """

    # Здесь можно добавить поля, специфичные только для создания, если они появятся.
    pass


# --- Схема для обновления объявления ---
class AdvertisementUpdate(BaseModel):
    """
    Схема для данных, необходимых при обновлении существующего объявления.
    Все поля опциональны, так как PATCH может обновлять только часть полей.
    """

    title: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Новый заголовок объявления"
    )
    description: Optional[str] = Field(
        None, max_length=500, description="Новое описание объявления"
    )
    # Цена также может быть обновлена, но валидация gt=0 остается важной, если поле передано
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

    # Валидатор для проверки, что хотя бы одно поле передано для обновления (опционально)
    # @field_validator('*', mode='before')
    # def check_at_least_one_value(cls, values):
    #     if not any(values.values()):
    #         raise ValueError("At least one field must be provided for update")
    #     return values


# --- Схема для отображения объявления ---
class Advertisement(AdvertisementBase):
    """
    Схема для данных объявления, возвращаемых API.
    Включает системные поля id, created_at, updated_at.
    """

    id: int = Field(..., description="Уникальный идентификатор объявления")
    created_at: datetime = Field(..., description="Дата и время создания")
    updated_at: datetime = Field(..., description="Дата и время последнего обновления")

    # Конфигурация для Pydantic: разрешить маппинг из атрибутов объекта (ORM mode)
    model_config = ConfigDict(from_attributes=True)


# --- Схема (или параметры) для поиска ---
class AdvertisementSearchParams(BaseModel):
    """
    Параметры для поиска, фильтрации, сортировки и пагинации объявлений.
    Используются как query-параметры в GET запросе.
    """

    title: Optional[str] = Field(
        None, description="Часть заголовка для поиска (регистронезависимый)"
    )
    author: Optional[str] = Field(
        None, description="Точное имя автора для фильтрации (регистронезависимый)"
    )
    min_price: Optional[Decimal] = Field(None, ge=0, description="Минимальная цена")
    max_price: Optional[Decimal] = Field(
        None, gt=0, description="Максимальная цена"
    )  # gt=0, так как бессмысленно искать объявления с макс. ценой 0
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
    )  # Ограничим limit

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
        return value.lower()  # Приводим к нижнему регистру для унификации

    @field_validator("max_price")
    def validate_price_range(cls, max_price, values):
        min_price = values.data.get("min_price")
        if min_price is not None and max_price is not None and max_price < min_price:
            raise ValueError("max_price cannot be less than min_price")
        return max_price
