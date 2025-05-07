# --- Этап 1: Сборка базового образа с зависимостями ---

FROM python:3.11-slim as builder

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /opt/app

# Устанавливаем переменные окружения Python для лучшей производительности
ENV PYTHONDONTWRITEBYTECODE 1  # Не создавать .pyc файлы
ENV PYTHONUNBUFFERED 1         # Выводить логи сразу, без буферизации

# Устанавливаем системные зависимости, необходимые для сборки некоторых Python пакетов
# Например, psycopg2-binary может требовать libpq-dev, а bcrypt - build-essential
# Для python:slim (Debian-based)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем Python зависимости в виртуальное окружение внутри образа
# Это помогает изолировать зависимости и уменьшить размер финального образа,
# если мы будем копировать только venv на следующий этап.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Обновляем pip и устанавливаем зависимости
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# --- Этап 2: Создание финального production-образа ---
FROM python:3.11-slim as final

WORKDIR /opt/app

# Устанавливаем те же переменные окружения Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Копируем системные зависимости, необходимые для работы приложения (libpq5 для psycopg2)
# Это важно, если на предыдущем этапе ставились -dev пакеты, а для рантайма нужны только библиотеки
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Копируем виртуальное окружение с зависимостями из этапа сборки
COPY --from=builder /opt/venv /opt/venv

# Устанавливаем PATH, чтобы использовать venv
ENV PATH="/opt/venv/bin:$PATH"

# Копируем код приложения в рабочую директорию
# Используем .dockerignore для исключения ненужных файлов
COPY ./app /opt/app/app
COPY ./migrations /opt/app/migrations 
COPY alembic.ini /opt/app/alembic.ini 

# Указываем пользователя, под которым будет запускаться приложение (не root)
# Сначала нужно создать пользователя и группу
RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser
RUN chown -R appuser:appuser /opt/app
USER appuser

# Порт, который слушает приложение внутри контейнера
EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && gunicorn -k aiohttp.worker.GunicornWebWorker --bind 0.0.0.0:8000 \"app.main:create_app()\""]