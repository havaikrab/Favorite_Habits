import os
from datetime import timedelta
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv(override=True)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG", "").lower() == "true"

USE_TELEGRAM_INTEGRATION = os.getenv("USE_TELEGRAM_INTEGRATION", "False").lower() == "true"

USE_TEST_WEBHOOK = os.getenv("USE_TEST_WEBHOOK", "False").lower() == "true"

CURRENT_SITE = os.getenv("CURRENT_SITE", "http://localhost:8000")

ALLOWED_HOSTS: list = ["localhost", "127.0.0.1"]

WEBHOOK_PATH = CURRENT_SITE + "/users/webhook/"

if DEBUG and USE_TELEGRAM_INTEGRATION and USE_TEST_WEBHOOK:
    WEBHOOK_PATH = os.getenv("TEST_WEBHOOK_PATH", "http://localhost:8000")
    parsed_url = urlparse(WEBHOOK_PATH)
    ALLOWED_HOSTS.append(parsed_url.hostname)
    WEBHOOK_PATH += "/users/webhook/"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    "django_celery_beat",
    "habits",
    "users",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}

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

AUTH_USER_MODEL = "users.CustomUser"

TIME_ZONE = os.getenv("LOCAL_TIME_ZONE", "UTC")

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = (BASE_DIR / "static",)

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework_simplejwt.authentication.JWTAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("ACCESS_TOKEN_LIFETIME", 5))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("REFRESH_TOKEN_LIFETIME", 1))),
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "False").lower() == "true"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

TG_BOT_LINK_HEAD = os.getenv("TG_BOT_LINK", "")
TG_BOT_ACCESS = os.getenv("TG_BOT_ACCESS")

REDIS_URL = "redis://" + os.getenv("REDIS_HOST", "127.0.0.1") + ":" + os.getenv("REDIS_PORT", "6379") + "/"

CACHE_DB = os.getenv("CACHE_DB", "1")
CACHES = {"default": {"BACKEND": "django.core.cache.backends.redis.RedisCache", "LOCATION": f"{REDIS_URL}{CACHE_DB}"}}

CELERY_BROKER_DB = os.getenv("CELERY_BROKER_DB", "2")
CELERY_BROKER_URL = f"{REDIS_URL}{CELERY_BROKER_DB}"
CELERY_RESULT_DB = os.getenv("CELERY_RESULT_DB", "3")
CELERY_RESULT_BACKEND = f"{REDIS_URL}{CELERY_RESULT_DB}"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = os.getenv("CELERY_TASK_TRACK_STARTED", "true").lower() == "true"
CELERY_TASK_TIME_LIMIT = int(os.getenv("CELERY_TASK_TIME_LIMIT", 63))
