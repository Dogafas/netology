# myshop/myshop/settings.py

from pathlib import Path
from decouple import config
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# --- Core Django Settings ---

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
# Читаем DEBUG из .env, по умолчанию False
DEBUG = config("DEBUG", default=False, cast=bool)

# Определяем ALLOWED_HOSTS из .env
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="127.0.0.1,localhost",
    cast=lambda v: [s.strip() for s in v.split(",")],
)


# --- Application definition ---

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Ваши приложения
    "cart.apps.CartConfig",
    "orders.apps.OrdersConfig",
    "payment.apps.PaymentConfig",
    "shop.apps.ShopConfig",
    "coupons.apps.CouponsConfig",
    # Сторонние приложения
    "rosetta",
    "parler",
    "localflavor",
    # 'debug_toolbar' будет добавлен ниже, если DEBUG=True
]

MIDDLEWARE = [
    # SecurityMiddleware должен быть одним из первых
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",  # Важно для i18n/l10n и parler
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # 'debug_toolbar.middleware.DebugToolbarMiddleware' будет добавлен ниже, если DEBUG=True
]

ROOT_URLCONF = "myshop.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],  # Можно добавить os.path.join(BASE_DIR, 'templates') если есть общие шаблоны
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "cart.context_processors.cart",  # Ваш контекст-процессор для корзины
            ],
        },
    },
]

WSGI_APPLICATION = "myshop.wsgi.application"
ASGI_APPLICATION = "myshop.asgi.application"  # Убедитесь, что asgi.py настроен, если планируете использовать ASGI/Channels


# --- Database Settings ---
# https://docs.djangoproject.com/en/stable/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
        "HOST": config(
            "POSTGRES_HOST"
        ),  # Должно быть имя сервиса из docker-compose, например 'db'
        "PORT": config("POSTGRES_PORT", default=5432, cast=int),
    }
}


# --- Password validation ---
# https://docs.djangoproject.com/en/stable/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# --- Internationalization ---
# https://docs.djangoproject.com/en/stable/topics/i18n/

LANGUAGE_CODE = "ru"  # Язык по умолчанию

LANGUAGES = [
    ("en", _("English")),
    ("ru", _("Russian")),
]

LOCALE_PATHS = [
    # os.path.join(BASE_DIR, "locale"), # Общие переводы проекта, если есть
    BASE_DIR / "locale",  # Используем Pathlib для путей
    BASE_DIR / "orders" / "locale",  # Переводы приложения orders
]

TIME_ZONE = "UTC"

USE_I18N = True  # Включаем систему переводов Django

USE_L10N = True  # Включаем локализацию форматов (устарело с Django 5.0, USE_FORMAT_LOCALIZATION=True)
USE_FORMAT_LOCALIZATION = True  # Для Django 5.0+

USE_TZ = True  # Включаем поддержку часовых поясов


# --- Static files (CSS, JavaScript, Images) ---
# https://docs.djangoproject.com/en/stable/howto/static-files/

STATIC_URL = "/static/"  # URL для статических файлов
STATIC_ROOT = (
    BASE_DIR / "staticfiles"
)  # Папка, куда collectstatic будет собирать все статические файлы для Nginx

# STATICFILES_DIRS = [BASE_DIR / "static"] # Если есть общая папка static в корне проекта

# --- Media files (User-uploaded content) ---
MEDIA_URL = "/media/"  # URL для медиа файлов
MEDIA_ROOT = BASE_DIR / "media"  # Папка для хранения загруженных пользователями файлов


# --- Default primary key field type ---
# https://docs.djangoproject.com/en/stable/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --- Cart Settings ---
CART_SESSION_ID = "cart"  # Ключ сессии для корзины


# --- Celery Settings ---
# Используем RabbitMQ как брокер сообщений
CELERY_BROKER_URL = config("RABBITMQ_BROKER_URL")
# Используем Redis как бэкенд для хранения результатов задач
# Используем отдельную базу Redis (по умолчанию 2)
REDIS_CELERY_DB = config(
    "REDIS_DB", default=2, cast=int
)  # REDIS_DB -> REDIS_CELERY_DB для ясности
CELERY_RESULT_BACKEND = f"redis://:{config('REDIS_PASSWORD', default='')}@{config('REDIS_HOST')}:{config('REDIS_PORT', cast=int)}/{REDIS_CELERY_DB}"

CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = config(
    "CELERY_TIMEZONE", default=TIME_ZONE
)  # Используем TIME_ZONE проекта по умолчанию
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True  # Попытка переподключения при старте


# --- Email Settings ---
# Используем config() для всех настроек Email
EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = config("EMAIL_HOST", default="localhost")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_USE_SSL = config(
    "EMAIL_USE_SSL", default=False, cast=bool
)  # Обычно TLS предпочтительнее SSL
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER)


# --- Stripe Payment Settings ---
STRIPE_PUBLISHABLE_KEY = config("STRIPE_PUBLISHABLE_KEY")
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY")
STRIPE_API_VERSION = config(
    "STRIPE_API_VERSION", default="2025-01-27.acacia"
)  # Проверьте актуальную версию API
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET")  # Для верификации вебхуков


# --- Redis Settings ---
# Глобальные настройки подключения Redis (используются CACHES и Recommender)
REDIS_HOST = config("REDIS_HOST", default="redis")
REDIS_PORT = config("REDIS_PORT", default=6379, cast=int)
REDIS_PASSWORD = config("REDIS_PASSWORD", default="")  # Пустая строка, если пароля нет

# --- Cache Settings (using Redis) ---
# Используем базу Redis (по умолчанию 0) для кэша Django
REDIS_CACHE_DB = config("REDIS_CACHE_DB", default=0, cast=int)
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_CACHE_DB}",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# --- Recommender Settings (using Redis) ---
# Используем отдельную базу Redis (по умолчанию 3) для системы рекомендаций
RECOMMENDER_REDIS_DB = config("RECOMMENDER_REDIS_DB", default=3, cast=int)
# Приложение recommender будет использовать REDIS_HOST, REDIS_PORT, REDIS_PASSWORD и RECOMMENDER_REDIS_DB


# --- django-parler Settings ---
PARLER_LANGUAGES = {
    None: (
        {"code": "en"},  # English
        {"code": "ru"},  # Russian
    ),
    "default": {
        "language_code": LANGUAGE_CODE,  # Используем основной язык сайта
        "fallbacks": [
            LANGUAGE_CODE,
            "en",
            "ru",
        ],  # Языки для отката, если перевод отсутствует
        "hide_untranslated": False,  # Показывать ли контент, если нет перевода
    },
}


# --- Security Settings ---

# Доверяем заголовкам от Nginx (или другого прокси)
# Важно, если Nginx терминирует SSL и передает запрос по HTTP
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# CSRF Protection
# Читаем доверенные источники из .env
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="",  # По умолчанию пусто, но в .env нужно указать!
    cast=lambda v: [
        s.strip() for s in v.split(",") if s.strip()
    ],  # Разделяем запятыми и убираем пустые строки
)
# Пример значения в .env: CSRF_TRUSTED_ORIGINS=https://your_domain.com,http://your_domain.com

# Production Security Settings (применяются только когда DEBUG = False)
if not DEBUG:
    SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=True, cast=bool)
    CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", default=True, cast=bool)
    # Редирект на HTTPS лучше делать на уровне Nginx
    # SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)

    # HSTS (HTTP Strict Transport Security) - Заставляет браузеры использовать только HTTPS
    # Убедитесь, что ВЕСЬ ваш сайт работает по HTTPS перед включением HSTS
    SECURE_HSTS_SECONDS = config(
        "SECURE_HSTS_SECONDS", default=2592000, cast=int
    )  # 30 дней для начала, потом можно увеличить
    SECURE_HSTS_INCLUDE_SUBDOMAINS = config(
        "SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True, cast=bool
    )
    SECURE_HSTS_PRELOAD = config(
        "SECURE_HSTS_PRELOAD", default=False, cast=bool
    )  # Установите True, только когда уверены и хотите добавить сайт в preload списки браузеров

    # Дополнительные меры безопасности
    # SECURE_BROWSER_XSS_FILTER = True # Заголовок X-XSS-Protection (устарел в современных браузерах)
    SECURE_CONTENT_TYPE_NOSNIFF = config(
        "SECURE_CONTENT_TYPE_NOSNIFF", default=True, cast=bool
    )


# --- Debug Toolbar Settings (только для режима DEBUG) ---
if DEBUG:
    # Включаем приложение
    INSTALLED_APPS.append("debug_toolbar")
    # Вставляем middleware после Security и Session, но перед Common
    # Найдем индекс CommonMiddleware, чтобы вставить перед ним
    try:
        common_middleware_index = MIDDLEWARE.index(
            "django.middleware.common.CommonMiddleware"
        )
        MIDDLEWARE.insert(
            common_middleware_index, "debug_toolbar.middleware.DebugToolbarMiddleware"
        )
    except ValueError:
        # Если CommonMiddleware нет (маловероятно), просто добавим в конец
        MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")

    # IP-адреса, с которых разрешен показ панели
    INTERNAL_IPS = [
        "127.0.0.1",
        # Добавьте IP вашего хоста, если Docker запущен на другой машине
        # или IP шлюза Docker сети (например, '172.17.0.1')
    ]

    # Настройки Email для отладки (вывод в консоль)
    # Раскомментируйте, если хотите видеть письма в консоли во время разработки
    # EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# --- Logging Configuration (Пример базовой настройки) ---
# TODO: Настроить логирование для продакшена (например, запись в файл или отправка в сервис)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",  # Уровень по умолчанию
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": config(
                "DJANGO_LOG_LEVEL", default="INFO"
            ),  # Уровень для логов Django
            "propagate": False,
        },
    },
}
