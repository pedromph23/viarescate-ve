"""
Configuración base de VíaRescate VE.

Contiene únicamente configuración común a todos los entornos.
Los valores sensibles se obtienen desde variables de entorno.
"""

from pathlib import Path

import environ


BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
)

# Carga .env si existe en desarrollo local.
env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(env_file)


SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="unsafe-development-key-change-me",
)

DEBUG = env("DJANGO_DEBUG")

ALLOWED_HOSTS = env.list(
    "DJANGO_ALLOWED_HOSTS",
    default=["127.0.0.1", "localhost"],
)


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.gis",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",

    # Aplicaciones VíaRescate VE.
    "core",
    "usuarios",
    "mapa",
    "operaciones",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
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
        "DIRS": [BASE_DIR / "templates"],
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
ASGI_APPLICATION = "config.asgi.application"


DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=(
            f"postgis://{env('DB_USER', default='viarescate')}:"
            f"{env('DB_PASSWORD', default='')}@"
            f"{env('DB_HOST', default='127.0.0.1')}:"
            f"{env('DB_PORT', default='5432')}/"
            f"{env('DB_NAME', default='viarescate_ve')}"
        ),
    )
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


LANGUAGE_CODE = env(
    "LANGUAGE_CODE",
    default="es-ve",
)

TIME_ZONE = env(
    "TIME_ZONE",
    default="America/Caracas",
)

USE_I18N = True
USE_TZ = True


STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]


MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Usuario personalizado del sistema.
AUTH_USER_MODEL = "usuarios.Usuario"


# Redis / Celery
REDIS_URL = env(
    "REDIS_URL",
    default="redis://127.0.0.1:6379/0",
)

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL


# Channels
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],
        },
    },
}


# Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}

# Autenticación web.
LOGIN_URL = "/usuarios/login/"
LOGIN_REDIRECT_URL = "/operaciones/"
LOGOUT_REDIRECT_URL = "/"
