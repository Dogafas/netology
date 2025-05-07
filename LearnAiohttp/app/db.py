# app\db.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from app.config import DATABASE_URL  # Импортируем DSN из конфига
from app.models.base import Base  # Импортируем базовый класс моделей

# Проверяем, что строка подключения задана
if DATABASE_URL is None:
    print(
        "DATABASE_URL is not set in the environment variables. "
        "Database connection cannot be established."
    )
    # В реальном приложении здесь лучше выбросить исключение
    # raise ValueError("DATABASE_URL environment variable not set.")
    # Для примера просто оставим engine = None, но приложение упадет при попытке доступа к БД
    async_engine = None
    AsyncSessionLocal = None
else:
    # Создаем асинхронный "движок" SQLAlchemy для взаимодействия с БД
    # echo=True полезно для отладки, т.к. выводит SQL-запросы в консоль
    async_engine = create_async_engine(DATABASE_URL, echo=True, future=True)

    # Создаем фабрику для асинхронных сессий SQLAlchemy
    # expire_on_commit=False предотвращает истечение объектов после коммита,
    # что часто требуется в асинхронных веб-приложениях.
    AsyncSessionLocal = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,  # Отключаем автофлаш для лучшего контроля в async context
        autocommit=False,
    )


# Асинхронный контекстный менеджер для получения сессии БД
# Это более современный подход по сравнению с функцией-генератором
@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Предоставляет асинхронную сессию SQLAlchemy в контекстном менеджере.

    Гарантирует правильное закрытие сессии.
    """
    if AsyncSessionLocal is None:
        raise RuntimeError("Database session factory is not initialized.")

    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            # При любой ошибке откатываем транзакцию
            await session.rollback()
            print(f"Session rollback due to error: {e}")  # Логирование ошибки
            raise  # Пробрасываем исключение дальше
        finally:
            # Сессия закрывается автоматически AsyncSessionLocal() контекстным менеджером
            pass  # Можно добавить логирование закрытия сессии, если нужно


async def init_db():
    """
    Создает все таблицы в базе данных на основе моделей SQLAlchemy.
    Эту функцию следует вызывать один раз при старте приложения (для разработки).
    """
    if async_engine is None:
        print("Database engine is not initialized. Cannot create tables.")
        return

    async with async_engine.begin() as conn:
        print(
            "Dropping all tables (for development)..."
        )  # Опционально, для чистой установки
        # await conn.run_sync(Base.metadata.drop_all) # Удаляет таблицы перед созданием
        print("Creating all tables...")
        # Создает таблицы, если они не существуют
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully.")


# Функция для закрытия соединения с БД (graceful shutdown)
async def close_db():
    """
    Закрывает соединение с базой данных.
    """
    if async_engine:
        print("Closing database connection pool...")
        await async_engine.dispose()
        print("Database connection pool closed.")
