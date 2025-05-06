# migrations\env.py
import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context


# Добавляем путь к нашему приложению в sys.path,
# чтобы Alembic мог найти наши модули (config, models)
# Это предполагает, что env.py находится в migrations/, а app/ - на уровень выше
# path/to/your/project/
#  - alembic.ini
#  - migrations/
#    - env.py
#  - app/
#    - models/
#    - config.py

# Определяем путь к корневой директории проекта
# (где находится папка app и alembic.ini)
# Это зависит от того, откуда запускаются команды alembic
# Если из корня проекта, то sys.path уже должен содержать корень.
# Но для надежности добавим:
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

# Импортируем наш Base из моделей и DATABASE_URL из конфига
from app.models.base import Base  # Путь к Base
from app.config import DATABASE_URL  # Путь к DATABASE_URL


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# ---> Указываем Alembic на метаданные наших моделей <---
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_database_url_for_alembic():
    """
    Возвращает DATABASE_URL, адаптированный для синхронного драйвера Alembic.
    Alembic использует psycopg2, поэтому URL должен быть postgresql://...
    Наш DATABASE_URL может быть postgresql+asyncpg://...
    """
    if DATABASE_URL is None:
        raise ValueError("DATABASE_URL is not set. Cannot configure Alembic.")

    # Заменяем asyncpg на psycopg2, если он есть в URL
    sync_db_url = DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")
    # Если используется просто postgresql://, то замена не нужна
    sync_db_url = sync_db_url.replace(
        "postgresql+aiosqlite", "sqlite"
    )  # Если бы был aiosqlite

    # Для отладки
    print(f"Using database URL for Alembic: {sync_db_url}")
    return sync_db_url


# ---> Устанавливаем sqlalchemy.url для Alembic из нашего конфига <---
# Это переопределит значение из alembic.ini, если оно там есть
config.set_main_option("sqlalchemy.url", get_database_url_for_alembic())


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # ---> Добавим это для поддержки сравнения типов в PostgreSQL <---
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # ---> Используем engine_from_config с нашей конфигурацией <---
    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section, {}
        ),  # Используем основной раздел из alembic.ini
        prefix="sqlalchemy.",  # sqlalchemy.url, sqlalchemy.pool_recycle, etc.
        poolclass=pool.NullPool,  # Не нужен пул для миграций
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # ---> Добавим это для поддержки сравнения типов в PostgreSQL <---
            compare_type=True,
            # Для PostgreSQL, если есть схемы кроме public
            # include_schemas=True, # Если нужно отслеживать таблицы в других схемах
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
