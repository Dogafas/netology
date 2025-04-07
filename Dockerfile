# Этап 1: Сборка с зависимостями сборки
# Используем Python 3.12 slim-версию на Debian Bullseye как базовый образ
FROM python:3.12-slim-bullseye AS builder

# Устанавливаем переменные окружения для Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем системные зависимости, необходимые для сборки Python-пакетов
# build-essential: Компиляторы C/C++
# libpq-dev: Заголовочные файлы для PostgreSQL клиента (для psycopg2)
# gettext: Для интернационализации Django (compilemessages)
# libjpeg-dev, zlib1g-dev: Для сборки Pillow (обработка изображений)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gettext \
    libjpeg-dev \
    zlib1g-dev \
    # Очищаем кэш apt после установки
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию внутри этого этапа
WORKDIR /app-build

# Обновляем pip до последней версии
RUN pip install --upgrade pip

# Копируем файл зависимостей (из папки myshop)
COPY ./myshop/requirements.txt .

# Создаем wheel-файлы для зависимостей. Это ускорит установку на следующем этапе
# и позволит удалить сборочные зависимости.
RUN pip wheel --no-cache-dir --wheel-dir=/wheels -r requirements.txt


# Этап 2: Финальный образ
# Используем тот же базовый образ для уменьшения размера
FROM python:3.12-slim-bullseye

# Устанавливаем переменные окружения для Python (повторно, т.к. это новый этап)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Создаем пользователя и группу 'appuser' для запуска приложения
RUN addgroup --system appuser && adduser --system --ingroup appuser appuser

# Устанавливаем системные зависимости времени выполнения
# libpq5: Runtime библиотеки для PostgreSQL клиента
# gettext: Runtime для i18n
# libjpeg62-turbo, zlib1g: Runtime для Pillow
# tini: Простой init-процесс для корректной обработки сигналов
# netcat-openbsd: Для команды 'nc' в entrypoint.sh
# Зависимости для WeasyPrint: Pango (текст/макет), PangoFT2 (шрифты), Cairo (графика), GDK-Pixbuf (изображения), Шрифты
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    gettext \
    libjpeg62-turbo \
    zlib1g \
    tini \
    netcat-openbsd \
    # Зависимости для WeasyPrint
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    fonts-noto \
    # Очищаем кэш apt и удаляем ненужные пакеты
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# Копируем предустановленные wheel-зависимости из этапа сборки 'builder'
COPY --from=builder /wheels /wheels

# Устанавливаем Python зависимости из локальных wheel-файлов
# Обратите внимание: сюда входят gunicorn, django-celery-beat, django-redis, weasyprint и др. из requirements.txt
RUN pip install --no-cache-dir /wheels/*

# Создаем основную рабочую директорию для приложения
WORKDIR /home/appuser/web

# Копируем скрипт точки входа (который теперь тоже использует nc)
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Копируем код нашего Django-проекта (папку 'myshop') в рабочую директорию
# Dockerfile находится в корне (shop-diplom), поэтому путь ./myshop корректен
COPY ./myshop /home/appuser/web/

# Меняем владельца всех файлов в рабочей директории и скрипта entrypoint на 'appuser'
# Это важно для безопасности и правильной работы с файлами (например, SQLite, если бы он использовался)
# Также это нужно для Gunicorn, если он будет писать pid-файлы или логи в эту директорию
RUN chown -R appuser:appuser /home/appuser/web /entrypoint.sh

# Переключаемся на непривилегированного пользователя
USER appuser

# Открываем порт 8000, на котором Gunicorn будет слушать входящие соединения
EXPOSE 8000

# Устанавливаем tini как точку входа, которая затем запустит наш скрипт entrypoint.sh
# Это обеспечивает правильное управление процессами внутри контейнера.
ENTRYPOINT ["/usr/bin/tini", "--", "/entrypoint.sh"]

# Команду по умолчанию (CMD) мы определим в docker-compose.yml,
# так как она будет разной для веб-сервера и Celery воркеров.
# Например: CMD ["gunicorn", "myshop.wsgi:application", "--bind", "0.0.0.0:8000"]