# app\security\dependencies.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from app.crud import user as crud_user
from app.security.auth import decode_access_token
from app.schemas import TokenData  # Используем схему для валидации payload


async def get_user_from_token(token: str, db: AsyncSession) -> Optional[User]:
    """
    Декодирует токен, извлекает ID пользователя и получает объект User из БД.

    Args:
        token: Строка с JWT.
        db: Асинхронная сессия SQLAlchemy.

    Returns:
        Объект User или None, если токен невалиден или пользователь не найден.
    """
    payload = decode_access_token(token)
    if not payload:
        return None

    # Валидируем payload с помощью Pydantic схемы TokenData (опционально, но полезно)
    try:
        token_data = TokenData(**payload)
    except Exception:  # Ловим ошибку валидации Pydantic
        print("Invalid token data structure")
        return None

    if token_data.user_id is None:
        return None

    # Получаем пользователя из БД по ID из токена
    user = await crud_user.get_user_by_id(db=db, user_id=token_data.user_id)
    return user
