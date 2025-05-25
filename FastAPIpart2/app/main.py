# app\main.py

import logging
from contextlib import asynccontextmanager
from typing import List, Annotated, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from . import crud, models, schemas, security
from .database import engine, Base, get_async_session, async_session_factory
from .config import settings
from datetime import timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_db_and_tables():
    logger.info("Attempting to create database tables...")
    async with engine.begin() as conn:
        # ВНИМАНИЕ: Это удалит существующие таблицы и создаст новые!
        # await conn.run_sync(
        #     Base.metadata.drop_all
        # )  # все существующие таблицы будут удалены
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables checked/created.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    # Создать пользователя-администратора по умолчанию при старте, если его нет
    async with async_session_factory() as db:  # Получаем сессию напрямую
        await create_default_admin_user(db)
    yield
    logger.info("Application shutdown.")


# --- Создание экземпляра FastAPI ---
app = FastAPI(
    title="Ads Service API",
    description="API для управления объявлениями и пользователями",
    version="0.2.0",  # Обновим версию :-)
    lifespan=lifespan,
)

# --- Зависимости ---
DBSession = Annotated[AsyncSession, Depends(get_async_session)]
CurrentUser = Annotated[models.User, Depends(security.get_current_active_user)]
# Опциональная зависимость для текущего пользователя (может быть None, если токен не предоставлен)
OptionalCurrentUser = Annotated[
    Optional[models.User], Depends(security.get_current_user)
]  # get_current_user может вернуть None или ошибку
AdminUser = Annotated[models.User, Depends(security.get_current_admin_user)]


# --- Вспомогательная функция для создания админа (при старте, опционально) ---

async def create_default_admin_user(db: AsyncSession):
    admin_username = getattr(settings, "ADMIN_USERNAME", "admin")
    admin_email = getattr(settings, "ADMIN_EMAIL", "admin@example.com")
    admin_password = getattr(settings, "ADMIN_PASSWORD", "adminpassword")

    # Проверяем по username
    user = await crud.get_user_by_username(db, username=admin_username)
    if not user:
        # Также стоит проверить по email, если username не найден,
        # т.к. email тоже уникальный
        user_by_email = await crud.get_user_by_email(db, email=admin_email)
        if not user_by_email:
            admin_in = schemas.UserCreate(
                username=admin_username,
                email=admin_email,
                password=admin_password,
                group=models.UserGroup.ADMIN,
            )
            await crud.create_user(db=db, user=admin_in)
            logger.info(f"Default admin user '{admin_username}' created.")
        else:
            logger.info(
                f"Default admin user with email '{admin_email}' already exists (found by email). Username in DB: {user_by_email.username}"
            )
    else:
        logger.info(
            f"Default admin user '{admin_username}' already exists (found by username)."
        )


# --- Эндпоинт для входа (Login) ---
@app.post(
    "/login",
    response_model=schemas.Token,
    summary="Получить JWT токен для аутентификации",
    tags=["Authentication"],
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DBSession,
):
    """
    Аутентифицирует пользователя по имени пользователя и паролю,
    возвращает JWT токен.
    """
    user = await crud.get_user_by_username(db, username=form_data.username)
    if not user or not security.verify_password(
        form_data.password, user.hashed_password
    ):
        logger.warning(f"Failed login attempt for username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={
            "sub": user.username
        },  # "sub" - это имя пользователя, которое будет в токене
        expires_delta=access_token_expires,
    )
    logger.info(f"User '{user.username}' logged in successfully.")
    return {"access_token": access_token, "token_type": "bearer"}


# --- Эндпоинты для пользователей (Users) ---


@app.post(
    "/user",
    response_model=schemas.User,
    status_code=status.HTTP_201_CREATED,
    summary="Создать нового пользователя",
    tags=["Users"],
)
async def create_new_user(
    user_in: schemas.UserCreate,
    db: DBSession,
    # Права: неавторизованный пользователь может создать пользователя (обычно с группой 'user')
    # Если создавать админа может только админ, то добавить: current_admin: AdminUser = Depends()
    # и проверять user_in.group
):
    """
    Создает нового пользователя. По умолчанию создается пользователь с группой 'user'.
    Если передана группа 'admin', это будет учтено (но эндпоинт должен быть защищен
    дополнительно, если создавать админов могут только админы).
    """
    # Проверка на существование пользователя с таким username или email
    existing_user = await crud.get_user_by_username(db, username=user_in.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    existing_email = await crud.get_user_by_email(db, email=user_in.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Если не админ пытается создать админа - запрещаем или понижаем до юзера
    # (В задании сказано: "неавторизованный пользователь ... Создание пользователя POST /user")
    # Это означает, что роль при создании может быть любой, если не защитить дополнительно.
    # Пока оставляем как есть, админ может быть создан любым.
    # Если нужно ограничение:
    # if user_in.group == models.UserGroup.ADMIN:
    #     # Попытка создать админа. Проверить, есть ли права (например, есть ли текущий пользователь и он админ)
    #     # Если это первый запуск, и админа создает система - ок.
    #     # Если эндпоинт публичный, то лучше по умолчанию ставить UserGroup.USER
    #     # user_in.group = models.UserGroup.USER # Принудительно, если не админ создает
    #     pass

    logger.info(f"Attempting to create user: {user_in.username}")
    db_user = await crud.create_user(db=db, user=user_in)
    logger.info(f"User '{db_user.username}' created with ID: {db_user.id}")
    return db_user


@app.get(
    "/user/{user_id}",
    response_model=schemas.User,
    summary="Получить пользователя по ID",
    tags=["Users"],
)
async def read_user_by_id(
    user_id: int,
    db: DBSession,
    # Права: неавторизованный пользователь может получить данные любого пользователя по ID
    # (Согласно задания). Если это не так, нужно добавить current_user: CurrentUser и проверки.
):
    logger.info(f"Fetching user with ID: {user_id}")
    db_user = await crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get(
    "/user",
    response_model=List[schemas.User],
    summary="Получить список пользователей (только для администраторов)",
    tags=["Users"],
    dependencies=[Depends(security.get_current_admin_user)],  # Только админ
)
async def read_all_users(
    db: DBSession,
    skip: int = 0,
    limit: int = 100,
):
    users = await crud.get_users(db, skip=skip, limit=limit)
    return users


@app.patch(
    "/user/{user_id}",
    response_model=schemas.User,
    summary="Обновить данные пользователя",
    tags=["Users"],
)
async def update_existing_user(
    user_id: int,
    user_in: schemas.UserUpdate,
    db: DBSession,
    current_user: CurrentUser,  # Текущий авторизованный пользователь
):
    logger.info(
        f"Attempting to update user ID: {user_id} by user {current_user.username}"
    )
    target_user = await crud.get_user(db, user_id=user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User to update not found")

    # Проверка прав:
    # 1. Админ может обновлять любого пользователя.
    # 2. Пользователь (user) может обновлять только свои данные.
    if (
        current_user.group != models.UserGroup.ADMIN
        and current_user.id != target_user.id
    ):
        raise HTTPException(
            status_code=403, detail="Not enough permissions to update this user"
        )

    # Дополнительная проверка: обычный пользователь не должен менять себе группу
    if user_in.group is not None and current_user.group != models.UserGroup.ADMIN:
        if user_in.group != target_user.group:  # Если пытаются изменить группу
            raise HTTPException(
                status_code=403, detail="Users cannot change their own or others' group"
            )
        # или можно просто проигнорировать user_in.group, если он не админ
        # user_in.group = None

    # Проверка уникальности username и email, если они меняются
    if user_in.username and user_in.username != target_user.username:
        existing_user = await crud.get_user_by_username(db, username=user_in.username)
        if (
            existing_user and existing_user.id != target_user.id
        ):  # Проверяем, что это не тот же юзер
            raise HTTPException(
                status_code=400, detail="New username already registered"
            )

    if user_in.email and user_in.email != target_user.email:
        existing_email = await crud.get_user_by_email(db, email=user_in.email)
        if existing_email and existing_email.id != target_user.id:
            raise HTTPException(status_code=400, detail="New email already registered")

    updated_user = await crud.update_user(
        db, user_id=user_id, user_update_data=user_in, current_user=current_user
    )
    if not updated_user:  # Эта проверка уже есть в crud.update_user, но для ясности
        raise HTTPException(
            status_code=404, detail="User not found (should not happen here)"
        )
    logger.info(f"User ID: {user_id} updated by {current_user.username}")
    return updated_user


@app.delete(
    "/user/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить пользователя",
    tags=["Users"],
)
async def delete_existing_user(user_id: int, db: DBSession, current_user: CurrentUser):
    logger.info(
        f"Attempting to delete user ID: {user_id} by user {current_user.username}"
    )
    target_user = await crud.get_user(db, user_id=user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User to delete not found")

    # Проверка прав:
    # 1. Админ может удалять любого пользователя.
    # 2. Пользователь (user) может удалять только себя.
    # 3. Нельзя удалить самого себя, если ты последний админ (опциональная сложная проверка)
    if (
        current_user.group != models.UserGroup.ADMIN
        and current_user.id != target_user.id
    ):
        raise HTTPException(
            status_code=403, detail="Not enough permissions to delete this user"
        )

    # Опционально: запретить удаление самого себя, если это текущий пользователь
    # if current_user.id == target_user.id:
    #     raise HTTPException(status_code=400, detail="Cannot delete yourself via this endpoint. Use a dedicated 'delete my account' feature or contact admin.")

    # deleted_user = await crud.delete_user(db, user_id=user_id)
    await crud.delete_user(db, user_id=user_id)
    # crud.delete_user вернет None, если пользователь не найден, но мы уже проверили
    logger.info(f"User ID: {user_id} deleted by {current_user.username}")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Эндпоинты для объявлений (Advertisements) ---


# Вспомогательная функция для проверки, может ли пользователь редактировать/удалять объявление
def check_advertisement_permissions(
    advertisement: models.Advertisement, user: models.User
):
    if user.group == models.UserGroup.ADMIN:
        return True  # Админ может все
    if advertisement.owner_id == user.id:
        return True  # Владелец может
    raise HTTPException(
        status_code=403, detail="Not enough permissions for this advertisement"
    )


@app.post(
    "/advertisement",
    response_model=schemas.Advertisement,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новое объявление (требуется аутентификация)",
    tags=["Advertisements"],
)
async def create_new_advertisement(
    advertisement_in: schemas.AdvertisementCreate,
    db: DBSession,
    current_user: CurrentUser,
):
    logger.info(
        f"User '{current_user.username}' attempting to create advertisement: {advertisement_in.title}"
    )
    db_advertisement = await crud.create_advertisement(
        db=db, advertisement=advertisement_in, owner_id=current_user.id
    )
    logger.info(
        f"Advertisement created with ID: {db_advertisement.id} by user {current_user.username}"
    )
    return db_advertisement


@app.get(
    "/advertisement/{advertisement_id}",
    response_model=schemas.Advertisement,
    summary="Получить объявление по ID (доступно всем)",
    tags=["Advertisements"],
)
async def read_advertisement(
    advertisement_id: int,
    db: DBSession,
    # current_user: OptionalCurrentUser = Depends(security.get_current_user) # Не обязательно, если доступно всем
    # Можно использовать OptionalCurrentUser, если логика зависит от того, авторизован ли юзер
):
    logger.info(f"Fetching advertisement with ID: {advertisement_id}")
    db_advertisement = await crud.get_advertisement(
        db=db, advertisement_id=advertisement_id
    )
    if db_advertisement is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return db_advertisement


@app.get(
    "/advertisement",
    response_model=List[schemas.Advertisement],
    summary="Поиск объявлений по параметрам (доступно всем)",
    tags=["Advertisements"],
)
async def search_all_advertisements(
    db: DBSession,
    params: schemas.AdvertisementSearchParams = Depends(),
):
    logger.info(f"Searching advertisements with params: {params.model_dump()}")
    advertisements = await crud.search_advertisements(db=db, params=params)
    return advertisements


@app.patch(
    "/advertisement/{advertisement_id}",
    response_model=schemas.Advertisement,
    summary="Обновить объявление по ID (владелец или админ)",
    tags=["Advertisements"],
)
async def update_existing_advertisement(
    advertisement_id: int,
    advertisement_data: schemas.AdvertisementUpdate,
    db: DBSession,
    current_user: CurrentUser,  # Требуется авторизация
):
    logger.info(
        f"User '{current_user.username}' attempting to update advertisement ID: {advertisement_id}"
    )
    db_advertisement = await crud.get_advertisement(
        db, advertisement_id=advertisement_id
    )  # get_advertisement уже загружает owner
    if not db_advertisement:
        raise HTTPException(status_code=404, detail="Advertisement not found")

    check_advertisement_permissions(db_advertisement, current_user)  # Проверка прав

    updated_advertisement = await crud.update_advertisement(
        db=db, advertisement_id=advertisement_id, advertisement_data=advertisement_data
    )
    # crud.update_advertisement сам вернет None если не найдет, но мы уже проверили
    logger.info(
        f"Advertisement ID: {advertisement_id} updated by user {current_user.username}"
    )
    return updated_advertisement


@app.delete(
    "/advertisement/{advertisement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить объявление по ID (владелец или админ)",
    tags=["Advertisements"],
)
async def delete_existing_advertisement(
    advertisement_id: int,
    db: DBSession,
    current_user: CurrentUser,  # Требуется авторизация
):
    logger.info(
        f"User '{current_user.username}' attempting to delete advertisement ID: {advertisement_id}"
    )
    db_advertisement = await crud.get_advertisement(
        db, advertisement_id=advertisement_id
    )
    if not db_advertisement:
        raise HTTPException(status_code=404, detail="Advertisement not found")

    check_advertisement_permissions(db_advertisement, current_user)  # Проверка прав

    await crud.delete_advertisement(db=db, advertisement_id=advertisement_id)
    logger.info(
        f"Advertisement ID: {advertisement_id} deleted by user {current_user.username}"
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
