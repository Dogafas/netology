# app\main.py

from aiohttp import web

# Импортируем функции для работы с БД и настройки роутов
from app.db import init_db, close_db
from app.routes import setup_routes

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
    app = web.Application()

    print("Configuring application...")

    # --- Настройка сигналов ---
    # Добавляем обработчики для событий старта и остановки приложения
    # Они будут вызывать наши функции для работы с БД.
    app.on_startup.append(init_database)
    app.on_shutdown.append(shutdown_database)

    # --- Настройка маршрутов ---
    # Вызываем функцию из routes.py для добавления всех эндпоинтов
    setup_routes(app)

    # --- Настройка Middleware (пока пропущено) ---
    # Сюда можно будет добавить middleware для обработки ошибок,
    # проверки авторизации (JWT), логирования и т.д.
    # app.middlewares.append(...)

    print("Application configured.")
    return app


# Точка входа для запуска приложения
if __name__ == "__main__":
    # Создаем экземпляр приложения
    app = create_app()

    # Запускаем приложение с помощью встроенного сервера aiohttp
    # host="0.0.0.0" делает сервер доступным извне контейнера Docker
    # port=8000 - стандартный порт для веб-сервисов
    print("Starting application server...")
    web.run_app(app, host="0.0.0.0", port=8000)
