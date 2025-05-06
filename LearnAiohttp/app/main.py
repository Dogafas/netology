# app\main.py

from aiohttp import web

# Импортируем функции для работы с БД и настройки роутов
from app.db import close_db
from app.routes import setup_routes
from app.middlewares import auth_middleware

# Можно импортировать и конфигурацию, если она нужна прямо здесь
# from app.config import ...


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
