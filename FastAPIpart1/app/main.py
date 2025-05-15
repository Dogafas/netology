import logging
from contextlib import asynccontextmanager
from typing import (
    List,
    Annotated,
)
from fastapi import FastAPI, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from . import crud, schemas
from .database import (
    engine,
    Base,
    get_async_session,
)  # Импортируем engine и Base для создания таблиц

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Функция для создания таблиц при старте ---
async def create_db_and_tables():
    """
    Асинхронно создает таблицы в базе данных на основе моделей SQLAlchemy.
    Вызывается один раз при старте приложения.
    """
    logger.info("Attempting to create database tables...")
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # Раскомментировать для удаления таблиц перед созданием (ВНИМАНИЕ: ПОТЕРЯ ДАННЫХ!)
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created (if they didn't exist).")


# --- Контекстный менеджер для управления жизненным циклом приложения ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер lifespan для выполнения действий при старте и остановке приложения.
    """
    await create_db_and_tables()  # Вызываем создание таблиц при старте
    yield
    logger.info("Application shutdown.")


# --- Создание экземпляра FastAPI ---
app = FastAPI(
    title="Ads Service API",
    description="API для управления объявлениями",
    version="0.1.0",
    lifespan=lifespan,
)

# --- Зависимость для получения сессии БД ---
DBSession = Annotated[AsyncSession, Depends(get_async_session)]


# --- Эндпоинты API ---


@app.post(
    "/advertisement",
    response_model=schemas.Advertisement,  # Схема для ответа
    status_code=status.HTTP_201_CREATED,  # Статус успешного создания
    summary="Создать новое объявление",
    tags=["Advertisements"],  # Группировка в документации
)
async def create_new_advertisement(
    advertisement: schemas.AdvertisementCreate,  # Данные из тела запроса
    db: DBSession,  # Получаем сессию БД через зависимость
):
    """
    Создает новое объявление с заголовком, описанием, ценой и автором.
    """
    logger.info(f"Attempting to create advertisement: {advertisement.title}")
    # Просто вызываем нашу CRUD функцию
    db_advertisement = await crud.create_advertisement(
        db=db, advertisement=advertisement
    )
    logger.info(f"Advertisement created with ID: {db_advertisement.id}")
    return db_advertisement


@app.get(
    "/advertisement/{advertisement_id}",
    response_model=schemas.Advertisement,
    summary="Получить объявление по ID",
    tags=["Advertisements"],
)
async def read_advertisement(advertisement_id: int, db: DBSession):
    """
    Получает детали одного объявления по его уникальному идентификатору.
    """
    logger.info(f"Fetching advertisement with ID: {advertisement_id}")
    db_advertisement = await crud.get_advertisement(
        db=db, advertisement_id=advertisement_id
    )
    if db_advertisement is None:
        logger.warning(f"Advertisement with ID: {advertisement_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Advertisement not found"
        )
    logger.info(f"Advertisement found: {db_advertisement.title}")
    return db_advertisement


@app.get(
    "/advertisement",
    response_model=List[schemas.Advertisement],  # Ответ - список объявлений
    summary="Поиск объявлений по параметрам",
    tags=["Advertisements"],
)
async def search_all_advertisements(
    # Используем Depends() для автоматического создания объекта схемы из query параметров
    db: DBSession,
    params: schemas.AdvertisementSearchParams = Depends(),
):
    """
    Осуществляет поиск объявлений с возможностью фильтрации по:
    - `title` (частичное совпадение, регистронезависимое)
    - `author` (точное совпадение, регистронезависимое)
    - `min_price`, `max_price` (диапазон цен)

    А также сортировки (`sort_by`, `order`) и пагинации (`skip`, `limit`).
    """
    logger.info(f"Searching advertisements with params: {params.model_dump()}")
    advertisements = await crud.search_advertisements(db=db, params=params)
    logger.info(f"Found {len(advertisements)} advertisements matching criteria.")
    return advertisements


@app.patch(
    "/advertisement/{advertisement_id}",
    response_model=schemas.Advertisement,
    summary="Обновить объявление по ID",
    tags=["Advertisements"],
)
async def update_existing_advertisement(
    advertisement_id: int,  # ID из пути
    advertisement_data: schemas.AdvertisementUpdate,  # Данные для обновления из тела
    db: DBSession,
):
    """
    Обновляет одно или несколько полей существующего объявления по его ID.
    Передавайте только те поля, которые нужно изменить.
    """
    logger.info(f"Attempting to update advertisement ID: {advertisement_id}")
    updated_advertisement = await crud.update_advertisement(
        db=db, advertisement_id=advertisement_id, advertisement_data=advertisement_data
    )
    if updated_advertisement is None:
        logger.warning(
            f"Update failed: Advertisement with ID {advertisement_id} not found"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Advertisement not found"
        )
    logger.info(f"Advertisement ID: {advertisement_id} updated successfully.")
    return updated_advertisement


@app.delete(
    "/advertisement/{advertisement_id}",
    status_code=status.HTTP_204_NO_CONTENT,  # Успешный ответ без тела
    summary="Удалить объявление по ID",
    tags=["Advertisements"],
)
async def delete_existing_advertisement(advertisement_id: int, db: DBSession):
    """
    Удаляет объявление по его уникальному идентификатору.
    """
    logger.info(f"Attempting to delete advertisement ID: {advertisement_id}")
    deleted_advertisement = await crud.delete_advertisement(
        db=db, advertisement_id=advertisement_id
    )
    if deleted_advertisement is None:
        logger.warning(
            f"Deletion failed: Advertisement with ID {advertisement_id} not found"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Advertisement not found"
        )
    logger.info(f"Advertisement ID: {advertisement_id} deleted successfully.")
    # Возвращаем пустой ответ со статусом 204
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Пример запуска uvicorn из кода (для отладки, обычно запускается из терминала)
# if __name__ == "__main__":
#     import uvicorn
#     # Важно: models должны быть импортированы до create_all, что гарантируется lifespan
#     # Убедимся, что модуль models загружен
#     from . import models
#
#     uvicorn.run(app, host="0.0.0.0", port=8000)
