# app\database.py

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
from .config import settings
# Создаем асинхронный движок SQLAlchemy
engine = create_async_engine(
    str(settings.DATABASE_URL_ASYNC),
    echo=False,  # Поставь True, если хочешь видеть генерируемые SQL запросы
    # pool_size=5, max_overflow=10 # Опциональные настройки пула соединений
)

# Создаем фабрику асинхронных сессий
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Создаем базовый класс для декларативных моделей SQLAlchemy
Base = declarative_base()


# Функция-генератор для предоставления сессии базы данных в эндпоинтах FastAPI
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость FastAPI для получения асинхронной сессии SQLAlchemy.
    Гарантирует закрытие сессии после использования.
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            pass
