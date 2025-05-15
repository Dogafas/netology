from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Sequence
from . import models
from . import schemas

# --- CREATE ---


async def create_advertisement(
    db: AsyncSession, advertisement: schemas.AdvertisementCreate
) -> models.Advertisement:
    """
    Создает новое объявление в базе данных.

    Args:
        db: Асинхронная сессия SQLAlchemy.
        advertisement: Данные нового объявления из схемы Pydantic.

    Returns:
        Созданный объект модели Advertisement.
    """
    # Создаем экземпляр модели SQLAlchemy на основе данных из схемы Pydantic
    db_advertisement = models.Advertisement(**advertisement.model_dump())

    # Добавляем объект в сессию
    db.add(db_advertisement)
    # Коммитим транзакцию, чтобы сохранить объект в БД
    await db.commit()
    # Обновляем объект из БД, чтобы получить сгенерированные значения (id, created_at)
    await db.refresh(db_advertisement)
    return db_advertisement


# --- READ ---


async def get_advertisement(
    db: AsyncSession, advertisement_id: int
) -> Optional[models.Advertisement]:
    """
    Получает одно объявление по его ID.

    Args:
        db: Асинхронная сессия SQLAlchemy.
        advertisement_id: ID объявления для поиска.

    Returns:
        Объект модели Advertisement или None, если не найден.
    """
    # Создаем запрос на выборку объявления по ID
    query = select(models.Advertisement).where(
        models.Advertisement.id == advertisement_id
    )
    # Выполняем запрос
    result = await db.execute(query)
    # Возвращаем первый найденный объект или None
    # scalars().first() извлекает первый столбец первой строки
    return result.scalars().first()


async def search_advertisements(
    db: AsyncSession, params: schemas.AdvertisementSearchParams
) -> Sequence[models.Advertisement]:
    """
    Ищет объявления по заданным параметрам с фильтрацией, сортировкой и пагинацией.

    Args:
        db: Асинхронная сессия SQLAlchemy.
        params: Параметры поиска из схемы Pydantic.

    Returns:
        Список (Sequence) найденных объектов модели Advertisement.
    """
    # Начинаем с базового запроса на выборку всех объявлений
    query = select(models.Advertisement)

    # --- Фильтрация ---
    filter_conditions = []
    if params.title:
        # Регистронезависимый поиск по подстроке в заголовке
        filter_conditions.append(models.Advertisement.title.ilike(f"%{params.title}%"))
    if params.author:
        # Регистронезависимый поиск по точному совпадению автора
        filter_conditions.append(
            func.lower(models.Advertisement.author) == func.lower(params.author)
        )
    if params.min_price is not None:
        filter_conditions.append(models.Advertisement.price >= params.min_price)
    if params.max_price is not None:
        filter_conditions.append(models.Advertisement.price <= params.max_price)

    # Применяем все условия фильтрации через AND
    if filter_conditions:
        query = query.where(
            and_(*filter_conditions)
        )  # Используем and_ для объединения условий

    # --- Сортировка ---
    sort_column = getattr(models.Advertisement, params.sort_by, None)
    # Проверяем, что поле для сортировки действительно существует в модели
    if sort_column is not None:
        if params.order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
    else:
        # Сортировка по умолчанию, если поле не указано или неверно (хотя схема должна это проверять)
        query = query.order_by(models.Advertisement.created_at.desc())

    # --- Пагинация ---
    query = query.offset(params.skip).limit(params.limit)

    # Выполняем итоговый запрос
    result = await db.execute(query)
    # Возвращаем все найденные объекты
    return result.scalars().all()


# --- UPDATE ---


async def update_advertisement(
    db: AsyncSession,
    advertisement_id: int,
    advertisement_data: schemas.AdvertisementUpdate,
) -> Optional[models.Advertisement]:
    """
    Обновляет существующее объявление по ID.

    Args:
        db: Асинхронная сессия SQLAlchemy.
        advertisement_id: ID обновляемого объявления.
        advertisement_data: Данные для обновления из схемы Pydantic (только переданные поля).

    Returns:
        Обновленный объект модели Advertisement или None, если объявление не найдено.
    """
    # Сначала получаем существующее объявление
    db_advertisement = await get_advertisement(db, advertisement_id)
    if db_advertisement is None:
        return None  # Объявление не найдено

    # Получаем данные для обновления как словарь, исключая не установленные поля
    update_data = advertisement_data.model_dump(exclude_unset=True)

    # Обновляем поля найденного объекта данными из словаря
    for key, value in update_data.items():
        setattr(db_advertisement, key, value)

    # Добавляем измененный объект в сессию (SQLAlchemy отследит изменения)
    db.add(db_advertisement)
    # Коммитим транзакцию
    await db.commit()
    # Обновляем объект, чтобы получить актуальные данные (например, updated_at)
    await db.refresh(db_advertisement)
    return db_advertisement


# --- DELETE ---


async def delete_advertisement(
    db: AsyncSession, advertisement_id: int
) -> Optional[models.Advertisement]:
    """
    Удаляет объявление по ID.

    Args:
        db: Асинхронная сессия SQLAlchemy.
        advertisement_id: ID удаляемого объявления.

    Returns:
        Удаленный объект модели Advertisement или None, если объявление не найдено.
    """
    # Находим объявление для удаления
    db_advertisement = await get_advertisement(db, advertisement_id)
    if db_advertisement is None:
        return None  # Объявление не найдено

    # Удаляем объект из сессии
    await db.delete(db_advertisement)
    # Коммитим транзакцию
    await db.commit()
    # Возвращаем удаленный объект (он все еще содержит данные до коммита)
    return db_advertisement
