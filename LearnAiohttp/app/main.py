# app\main.py

from aiohttp import web

# Импортируем функции для работы с БД и настройки роутов
from app.db import init_db, close_db
from app.routes import setup_routes
from app.middlewares import auth_middleware

# Можно импортировать и конфигурацию, если она нужна прямо здесь
# from app.config import ...


async def init_database(app: web.Application):
    """Сигнал для инициализации базы данных при старте приложения."""
    print("Application startup: initializing database...")
    # В реальном приложении здесь может быть более сложная логика,
    # например, ожидание доступности БД перед попыткой инициализации.
    try:
        await init_db()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error during database initialization: {e}")
        # В зависимости от политики, можно остановить запуск приложения
        # raise e


async def shutdown_database(app: web.Application):
    """Сигнал для закрытия соединения с БД при остановке приложения."""
    print("Application shutdown: closing database connection...")
    await close_db()
    print("Database connection closed.")


def create_app() -> web.Application:
    """
    Создает и конфигурирует экземпляр приложения aiohttp.
    """
    # ---> Добавляем middleware в список <---
    app = web.Application(middlewares=[auth_middleware])

    print("Configuring application...")

    # --- Настройка сигналов ---
    app.on_startup.append(init_database)
    app.on_shutdown.append(shutdown_database)

    # --- Настройка маршрутов ---
    setup_routes(app)

    print("Application configured.")
    return app


# Точка входа для запуска приложения
if __name__ == "__main__":
    app = create_app()
    print("Starting application server...")
    web.run_app(app, host="0.0.0.0", port=8000)
