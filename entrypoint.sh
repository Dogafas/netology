#!/bin/sh

# Выходим сразу, если команда завершилась с ошибкой
set -e

# --- Используем ИМЕНА СЕРВИСОВ и ВНУТРЕННИЕ ПОРТЫ ---
DB_HOST=${POSTGRES_HOST:-db} # Имя сервиса из docker-compose, по умолчанию 'db'
DB_PORT=${POSTGRES_PORT:-5432} # Внутренний порт Postgres, по умолчанию 5432

RABBITMQ_SERVICE_HOST=${RABBITMQ_HOST:-rabbitmq} # Имя сервиса RabbitMQ, по умолчанию 'rabbitmq'
RABBITMQ_SERVICE_PORT=5672 # Стандартный внутренний порт AMQP

REDIS_SERVICE_HOST=${REDIS_HOST:-redis} # Имя сервиса Redis, по умолчанию 'redis'
REDIS_SERVICE_PORT=${REDIS_PORT:-6379} # Внутренний порт Redis, по умолчанию 6379
# ----------------------------------------------------

# Функция для ожидания доступности базы данных PostgreSQL
wait_for_postgres() {
    echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."
    # Используем имя сервиса и внутренний порт
    while ! nc -z "$DB_HOST" "$DB_PORT"; do
        echo -n "."
        sleep 2
    done
    echo "PostgreSQL started"
}

# Функция для ожидания доступности RabbitMQ
wait_for_rabbitmq() {
    echo "Waiting for RabbitMQ at $RABBITMQ_SERVICE_HOST:$RABBITMQ_SERVICE_PORT..."
    # Используем имя сервиса и внутренний порт
    while ! nc -z "$RABBITMQ_SERVICE_HOST" "$RABBITMQ_SERVICE_PORT"; do
        echo -n "."
        sleep 2
    done
    echo "RabbitMQ started"
}

# Функция для ожидания доступности Redis
wait_for_redis() {
    echo "Waiting for Redis at $REDIS_SERVICE_HOST:$REDIS_SERVICE_PORT..."
    # Используем имя сервиса и внутренний порт
    while ! nc -z "$REDIS_SERVICE_HOST" "$REDIS_SERVICE_PORT"; do
        echo -n "."
        sleep 2
    done
    echo "Redis started"
}


# Определяем, какая команда должна быть запущена
case "$1" in
    web)
        echo "Running WEB setup..."
        wait_for_postgres
        wait_for_rabbitmq # Если веб-серверу нужно общаться с RabbitMQ при старте
        wait_for_redis    # Если веб-серверу нужен Redis при старте

        echo "Applying database migrations..."
        python manage.py migrate --noinput

        echo "Collecting static files..."
        python manage.py collectstatic --noinput --clear

        echo "Compiling translations..."
        # Добавляем || true, чтобы ошибки compilemessages не останавливали запуск Gunicorn
        # Вы должны исправить ошибки в .po файлах позже
        python manage.py compilemessages || true

        echo "Starting Gunicorn..."
        # Запускаем Gunicorn на внутреннем порту 8000
        exec gunicorn myshop.wsgi:application --bind 0.0.0.0:8000 --workers $GUNICORN_WORKERS --log-level info
        ;;

    celery_worker)
        echo "Running CELERY WORKER setup..."
        wait_for_postgres
        wait_for_rabbitmq
        wait_for_redis

        echo "Starting Celery worker..."
        exec celery -A myshop worker --loglevel=info
        ;;



    celery_flower)
        echo "Running CELERY FLOWER setup..."
        # Flower обычно достаточно дождаться брокера и бэкенда результатов (если он настроен)
        wait_for_rabbitmq
        wait_for_redis # Flower может показывать результаты из Redis

        echo "Starting Celery Flower..."
        # Flower слушает на порту 5555 внутри контейнера
        exec celery -A myshop flower --loglevel=info --url_prefix=flower --port=5555
        ;;

    *)
        # Если передана другая команда, просто выполняем ее
        echo "Executing command: $@"
        exec "$@"
        ;;
esac