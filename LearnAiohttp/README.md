python -m app.main

Основные команды Alembic (краткая справка)

alembic current: Показывает текущую ревизию (примененную миграцию).
alembic history: Показывает историю миграций.
alembic revision -m "описание_изменений" --autogenerate: Создать новую миграцию на основе изменений в моделях. Делать это каждый раз, когда меняешь модели.
alembic upgrade head: Применить все непримененные миграции.
alembic upgrade +1: Применить следующую миграцию.
alembic upgrade <revision_id>: Обновиться до конкретной ревизии.
alembic downgrade -1: Откатить последнюю миграцию.
alembic downgrade base: Откатить все миграции.
