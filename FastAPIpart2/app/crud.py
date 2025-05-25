# app/crud.py

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, Sequence
from . import models
from . import schemas
from .security import get_password_hash  # Импортируем функцию для хеширования пароля

# --- CRUD для пользователей ---


async def get_user(db: AsyncSession, user_id: int) -> Optional[models.User]:
    """Получает пользователя по его ID."""
    query = select(models.User).where(models.User.id == user_id)
    result = await db.execute(query)
    return result.scalars().first()


async def get_user_by_username(
    db: AsyncSession, username: str
) -> Optional[models.User]:
    """Получает пользователя по его имени пользователя (username)."""
    query = select(models.User).where(models.User.username == username)
    result = await db.execute(query)
    return result.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[models.User]:
    """Получает пользователя по его email."""
    query = select(models.User).where(models.User.email == email)
    result = await db.execute(query)
    return result.scalars().first()


async def get_users(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> Sequence[models.User]:
    """Получает список пользователей с пагинацией."""
    query = select(models.User).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def create_user(db: AsyncSession, user: schemas.UserCreate) -> models.User:
    """Создает нового пользователя."""
    hashed_password = get_password_hash(user.password)
    # Создаем объект модели, не передавая password напрямую, а передавая hashed_password
    # и остальные поля из user.model_dump(), исключая 'password'
    user_data_for_model = user.model_dump(exclude={"password"})
    db_user = models.User(**user_data_for_model, hashed_password=hashed_password)

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update_user(
    db: AsyncSession,
    user_id: int,
    user_update_data: schemas.UserUpdate,
    current_user: models.User,
) -> Optional[models.User]:
    """
    Обновляет данные пользователя.
    Администратор может менять группу пользователя.
    Обычный пользователь не может менять свою группу.
    """
    db_user = await get_user(db, user_id)
    if not db_user:
        return None

    update_data = user_update_data.model_dump(exclude_unset=True)

    # Если обновляется пароль, его нужно хешировать
    if "password" in update_data and update_data["password"]:
        hashed_password = get_password_hash(update_data["password"])
        update_data["hashed_password"] = hashed_password
        del update_data[
            "password"
        ]  # Удаляем plain password из данных для обновления модели
    elif "password" in update_data:  # Если password передан как None или пустая строка
        del update_data["password"]  # Не обновляем пароль

    # Проверка прав на изменение группы
    if "group" in update_data:
        if current_user.group != models.UserGroup.ADMIN:
            # Если текущий пользователь не админ, он не может менять группу
            # (даже свою). Это можно изменить, если юзер должен иметь право понизить себя.
            # Но повысить точно не должен. Проще запретить юзеру менять группу вообще.
            # Или, если пользователь пытается изменить свою группу, не будучи админом
            if db_user.id == current_user.id and update_data["group"] != db_user.group:
                # Если не админ пытается сменить группу себе или другому
                del update_data["group"]  # Игнорируем попытку изменения группы
            elif (
                db_user.id != current_user.id
            ):  # Не админ пытается сменить группу другому
                del update_data["group"]

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user(db: AsyncSession, user_id: int) -> Optional[models.User]:
    """Удаляет пользователя по ID."""
    db_user = await get_user(db, user_id)
    if not db_user:
        return None

    await db.delete(db_user)
    await db.commit()
    return db_user  # Возвращаем удаленный объект (до коммита он еще доступен)


# --- CRUD для объявлений ---


async def create_advertisement(
    db: AsyncSession,
    advertisement: schemas.AdvertisementCreate,
    owner_id: int,  # Добавили owner_id
) -> models.Advertisement:
    """
    Создает новое объявление в базе данных.
    Теперь требует owner_id.
    """
    db_advertisement = models.Advertisement(
        **advertisement.model_dump(), owner_id=owner_id  # Присваиваем ID владельца
    )
    db.add(db_advertisement)
    await db.commit()
    await db.refresh(db_advertisement)
    return db_advertisement


async def get_advertisement(
    db: AsyncSession, advertisement_id: int
) -> Optional[models.Advertisement]:
    # Загружаем связанный объект owner для отображения в схеме Advertisement
    query = (
        select(models.Advertisement)
        .options(selectinload(models.Advertisement.owner))
        .where(models.Advertisement.id == advertisement_id)
    )
    result = await db.execute(query)
    return result.scalars().first()


async def search_advertisements(
    db: AsyncSession, params: schemas.AdvertisementSearchParams
) -> Sequence[models.Advertisement]:
    query = select(models.Advertisement).options(
        selectinload(models.Advertisement.owner)
    )  # Добавили selectinload

    filter_conditions = []
    if params.title:
        filter_conditions.append(models.Advertisement.title.ilike(f"%{params.title}%"))
    if params.author:  # Поиск по полю author остается
        filter_conditions.append(
            func.lower(models.Advertisement.author) == func.lower(params.author)
        )
    if params.min_price is not None:
        filter_conditions.append(models.Advertisement.price >= params.min_price)
    if params.max_price is not None:
        filter_conditions.append(models.Advertisement.price <= params.max_price)

    if filter_conditions:
        query = query.where(and_(*filter_conditions))

    sort_column = getattr(models.Advertisement, params.sort_by, None)
    if sort_column is not None:
        if params.order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(models.Advertisement.created_at.desc())

    query = query.offset(params.skip).limit(params.limit)
    result = await db.execute(query)
    return result.scalars().all()


async def update_advertisement(
    db: AsyncSession,
    advertisement_id: int,
    advertisement_data: schemas.AdvertisementUpdate,
) -> Optional[models.Advertisement]:
    # При обновлении также полезно загрузить владельца, если это будет нужно для проверок прав
    query = (
        select(models.Advertisement)
        .options(selectinload(models.Advertisement.owner))
        .where(models.Advertisement.id == advertisement_id)
    )
    result = await db.execute(query)
    db_advertisement = result.scalars().first()

    if db_advertisement is None:
        return None

    update_data = advertisement_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_advertisement, key, value)

    db.add(db_advertisement)
    await db.commit()
    await db.refresh(db_advertisement)
    return db_advertisement


async def delete_advertisement(
    db: AsyncSession, advertisement_id: int
) -> Optional[models.Advertisement]:
    db_advertisement = await get_advertisement(
        db, advertisement_id
    )  # get_advertisement уже делает selectinload
    if db_advertisement is None:
        return None

    await db.delete(db_advertisement)
    await db.commit()
    return db_advertisement
