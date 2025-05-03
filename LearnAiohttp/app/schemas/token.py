# app\schemas\token.py
from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """Схема для ответа с JWT токеном."""

    access_token: str
    token_type: str = "bearer"  # Стандартное значение для типа токена


class TokenData(BaseModel):
    """Схема для данных, хранящихся внутри JWT токена."""

    user_id: Optional[int] = None  # Идентификатор пользователя
    # Можно добавить другие поля, если нужно (например, email, роли)
