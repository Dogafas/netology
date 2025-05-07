# app\crud\advertisement.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload  # Для жадной загрузки владельца

from app.models import Advertisement
from app.schemas import AdvertisementCreate, AdvertisementUpdate


async def create_advertisement(
    db: AsyncSession, *, ad_in: AdvertisementCreate, owner_id: int
) -> Advertisement:
    """
    Создает новое объявление в БД.

    Args:
        db: Асинхронная сессия SQLAlchemy.
        ad_in: Схема Pydantic с данными для создания объявления (title, description).
        owner_id: ID пользователя-владельца.

    Returns:
        Созданный объект Advertisement.
    """
    db_ad = Advertisement(
        title=ad_in.title, description=ad_in.description, owner_id=owner_id
    )
    db.add(db_ad)
    await db.commit()
    await db.refresh(db_ad)
    return db_ad


async def get_advertisement_by_id(
    db: AsyncSession, ad_id: int
) -> Optional[Advertisement]:
    """
    Получает объявление из БД по его ID.
    Загружает связанный объект пользователя (owner).

    Args:
        db: Асинхронная сессия SQLAlchemy.
        ad_id: Идентификатор объявления.

    Returns:
        Объект Advertisement (с загруженным владельцем) или None.
    """
    # Используем selectinload для "жадной" загрузки связанного пользователя
    # Это предотвращает дополнительные запросы к БД при доступе к ad.owner
    stmt = (
        select(Advertisement)
        .options(selectinload(Advertisement.owner))
        .filter(Advertisement.id == ad_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_advertisements(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> List[Advertisement]:
    """
    Получает список объявлений из БД с пагинацией.

    Args:
        db: Асинхронная сессия SQLAlchemy.
        skip: Количество пропускаемых записей.
        limit: Максимальное количество возвращаемых записей.

    Returns:
        Список объектов Advertisement.
    """
    stmt = (
        select(Advertisement)
        .offset(skip)
        .limit(limit)
        .order_by(Advertisement.created_at.desc())
    )
    # Можно добавить selectinload(Advertisement.owner), если в списке нужны данные владельцев
    result = await db.execute(stmt)
    return result.scalars().all()


async def update_advertisement(
    db: AsyncSession, *, db_ad: Advertisement, ad_in: AdvertisementUpdate
) -> Advertisement:
    """
    Обновляет существующее объявление в БД.

    Args:
        db: Асинхронная сессия SQLAlchemy.
        db_ad: Существующий объект Advertisement из БД.
        ad_in: Схема Pydantic с обновляемыми данными (title, description).

    Returns:
        Обновленный объект Advertisement.
    """
    # Получаем данные из схемы как словарь
    update_data = ad_in.model_dump(
        exclude_unset=True
    )  # В Pydantic V1: ad_in.dict(exclude_unset=True)

    # Обновляем поля модели данными из словаря
    for field, value in update_data.items():
        setattr(db_ad, field, value)

    db.add(db_ad)  # Добавляем измененный объект в сессию
    await db.commit()
    await db.refresh(db_ad)
    return db_ad


async def delete_advertisement(
    db: AsyncSession, *, db_ad: Advertisement
) -> Advertisement:
    """
    Удаляет объявление из БД.

    Args:
        db: Асинхронная сессия SQLAlchemy.
        db_ad: Объект Advertisement для удаления.

    Returns:
        Удаленный объект Advertisement.
    """
    await db.delete(db_ad)
    await db.commit()
    # После удаления объект db_ad больше не связан с сессией, refresh не нужен
    # Возвращаем объект как есть (он все еще содержит данные удаленной записи)
    return db_ad
