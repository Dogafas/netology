# app\crud\user.py

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload  # Для жадной загрузки связей, если понадобится

from app.models import User
from app.schemas import UserCreate  # Используем схему для входных данных


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    Получает пользователя из БД по его ID.

    Args:
        db: Асинхронная сессия SQLAlchemy.
        user_id: Идентификатор пользователя.

    Returns:
        Объект User или None, если пользователь не найден.
    """
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    Получает пользователя из БД по его email.

    Args:
        db: Асинхронная сессия SQLAlchemy.
        email: Email пользователя.

    Returns:
        Объект User или None, если пользователь не найден.
    """
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession, *, user_in: UserCreate, password_hash: str
) -> User:
    """
    Создает нового пользователя в БД.

    Args:
        db: Асинхронная сессия SQLAlchemy.
        user_in: Схема Pydantic с данными для создания пользователя (email).
        password_hash: Уже хешированный пароль пользователя.

    Returns:
        Созданный объект User.
    """
    # Создаем экземпляр модели SQLAlchemy
    db_user = User(
        email=user_in.email,
        password_hash=password_hash,  # Сохраняем хеш, а не открытый пароль
    )
    # Добавляем нового пользователя в сессию
    db.add(db_user)
    # Коммитим изменения в базу данных
    await db.commit()
    # Обновляем объект db_user данными из базы (например, полученным ID)
    await db.refresh(db_user)
    return db_user


# Функции update_user и delete_user можно добавить по аналогии, если они понадобятся
