from django.utils.translation import gettext_lazy as _

import os
from pathlib import Path
from decouple import config


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

SECRET_KEY = config("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="127.0.0.1,localhost",
    cast=lambda v: [s.strip() for s in v.split(",")],
)


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "cart.apps.CartConfig",
    "orders.apps.OrdersConfig",
    "payment.apps.PaymentConfig",
    "shop.apps.ShopConfig",
    "debug_toolbar",
    "coupons.apps.CouponsConfig",
    "rosetta",
    "parler",
    "localflavor",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "myshop.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "cart.context_processors.cart",
            ],
        },
    },
]

WSGI_APPLICATION = "myshop.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
        "HOST": config("POSTGRES_HOST"),  # Должно быть 'db' для Docker Compose
        "PORT": config("POSTGRES_PORT", default=5432, cast=int),
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


LANGUAGES = [
    ("en", _("English")),
    ("ru", _("Russian")),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, "orders", "locale"),
    os.path.join(BASE_DIR, "locale"),
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"
# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
# MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATIC_ROOT = BASE_DIR / "staticfiles"
# STATIC_ROOT = BASE_DIR / "static"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CART_SESSION_ID = "cart"


CELERY_BROKER_URL = config("RABBITMQ_BROKER_URL")
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = config("CELERY_TIMEZONE", default="UTC")
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Email Settings
# Используем config() для всех настроек Email
EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", default=False, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER)

# конфигурация платежной системы
STRIPE_PUBLISHABLE_KEY = config("STRIPE_PUBLISHABLE_KEY")
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY")
STRIPE_API_VERSION = config("STRIPE_API_VERSION", default="2025-01-27.acacia")
# подтверждение оплаты от stripe "payment_intent.succeeded"
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET")

INTERNAL_IPS = [
    "127.0.0.1",
]

# настройки redis
# Redis settings for Cache (или другие цели, кроме Celery)
# Используем config()
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        # Используем базу данных Redis, отличную от Celery (например, 0)
        "LOCATION": f"redis://:{config('REDIS_PASSWORD')}@{config('REDIS_HOST')}:{config('REDIS_PORT', cast=int)}/{config('REDIS_DB', default=0, cast=int)}",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# --- Настройки Redis для прямого использования (например, Recommender) ---
# Читаем из переменных окружения, используя те же имена, что и для CACHES/CELERY
REDIS_HOST = config("REDIS_HOST", default="redis")
REDIS_PORT = config("REDIS_PORT", default=6379, cast=int)
REDIS_PASSWORD = config(
    "REDIS_PASSWORD", default=None
)  # Будет None, если в .env нет пароля

# !!! ВАЖНО: Используйте ОТДЕЛЬНУЮ базу данных Redis для Recommender,
# чтобы не конфликтовать с кэшем Django (обычно БД 0) и результатами Celery (мы выбрали БД 2).
# Например, используем БД 3 для Recommender.
RECOMMENDER_REDIS_DB = config("RECOMMENDER_REDIS_DB", default=3, cast=int)

# настройки parler
PARLER_LANGUAGES = {
    None: (
        {
            "code": "en",
        },
        {
            "code": "ru",
        },
    ),
    "default": {
        "fallbacks": "ru",
        "hide_untranslated": False,
    },
}

# Используем другую БД Redis для Celery
REDIS_CELERY_DB = config("REDIS_DB", default=2, cast=int)
CELERY_RESULT_BACKEND = f"redis://:{config('REDIS_PASSWORD')}@{config('REDIS_HOST')}:{config('REDIS_PORT', cast=int)}/{REDIS_CELERY_DB}"

# Настройки CSRF
# Добавляем URL, с которого приходят запросы через Nginx
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",  # Добавим и IP на всякий случай
    # Если будете использовать другой хост/домен, добавьте и его
    # 'http://your_domain.com',
    # 'https://your_domain.com', # Если будет HTTPS
]

# Настройки для работы за прокси-сервером (Nginx)
USE_X_FORWARDED_HOST = True  # Доверять заголовку X-Forwarded-Host (или Host от Nginx)
USE_X_FORWARDED_PORT = True  # Доверять заголовку X-Forwarded-Port
SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)  # Для определения https за прокси (если будете использовать HTTPS)
