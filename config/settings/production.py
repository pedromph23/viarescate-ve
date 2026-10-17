import os
"""
Configuración de producción de VíaRescate VE.

Todos los valores sensibles y dependientes del entorno se obtienen
desde variables de entorno.
"""

from .base import *  # noqa: F403,F401


DEBUG = False


ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])

CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])


# ---------------------------------------------------------------------------
# Seguridad (Vercel termina TLS antes de llegar a Django)
# ---------------------------------------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"


# La clave debe ser obligatoria en producción.
SECRET_KEY = env("DJANGO_SECRET_KEY")


# ---------------------------------------------------------------------------
# Static files con WhiteNoise (Vercel no sirve /static/ por defecto)
# ---------------------------------------------------------------------------
STORAGES["staticfiles"] = {  # noqa: F405
    "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
}


# ---------------------------------------------------------------------------
# Media files
# ---------------------------------------------------------------------------
# Por defecto usamos S3 (Supabase Storage). Si no hay credenciales,
# se cae al filesystem local (efímero en Vercel, pero útil para probar).
# ---------------------------------------------------------------------------
# Supabase Storage — variables a nivel de módulo para que storage.py las lea
# ---------------------------------------------------------------------------
SUPABASE_S3_PUBLIC_URL = env("SUPABASE_S3_PUBLIC_URL", default="")
SUPABASE_S3_BUCKET = env("SUPABASE_S3_BUCKET", default="media")

if env.bool("USE_S3_MEDIA", default=False):
    STORAGES["default"] = {  # noqa: F405
        "BACKEND": "operaciones.storage.SupabasePublicStorage",
        "OPTIONS": {
            "access_key": env("SUPABASE_S3_ACCESS_KEY"),
            "secret_key": env("SUPABASE_S3_SECRET_KEY"),
            "bucket_name": SUPABASE_S3_BUCKET,
            "endpoint_url": env("SUPABASE_S3_ENDPOINT"),
            "region_name": env("SUPABASE_S3_REGION", default="us-east-1"),
            "addressing_style": "path",
            "querystring_auth": False,
            "file_overwrite": False,
        },
    }
    MEDIA_URL = SUPABASE_S3_PUBLIC_URL or MEDIA_URL  # noqa: F405


# ---------------------------------------------------------------------------
# Channels: Vercel no ejecuta Redis persistente.
# En producción usamos in-memory (SSE/polling, no WebSockets reales).
# ---------------------------------------------------------------------------
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}


# ---------------------------------------------------------------------------
# Logging a stdout (Vercel lo captura automáticamente)
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "[{levelname}] {name}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.security": {"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
}


# La aplicación detrás de un proxy confiable puede utilizar
# X-Forwarded-For para registrar la IP original del cliente.
AUDIT_TRUST_PROXY_HEADERS = env.bool(
    "AUDIT_TRUST_PROXY_HEADERS",
    default=True,
)


# ---------------------------------------------------------------------------
# GeoDjango: rutas a librerías nativas provistas por vercel-python-gis-modern
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# GeoDjango: rutas a librerías nativas provistas por vercel-python-gis-modern
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# GeoDjango: rutas a librerías nativas provistas por vercel-python-gis-runtime
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# GeoDjango: rutas a librerías nativas provistas por vercel-python-gis
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# GeoDjango: rutas a librerías nativas provistas por vercel-python-gis-runtime
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# GeoDjango: rutas a librerías nativas provistas por vercel-python-gis-modern
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# GeoDjango: rutas a librerías nativas provistas por vercel-python-gis-modern
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# GeoDjango: rutas a librerías nativas provistas por vercel-python-gis-runtime
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# GeoDjango: rutas a librerías nativas, resueltas en api/index.py
# ---------------------------------------------------------------------------
GDAL_LIBRARY_PATH = os.environ.get("GDAL_LIBRARY_PATH", "libgdal.so")
GEOS_LIBRARY_PATH = os.environ.get("GEOS_LIBRARY_PATH", "libgeos_c.so.1")
PROJ_LIBRARY_PATH = os.environ.get("PROJ_LIBRARY_PATH", "libproj.so")


# ---------------------------------------------------------------------------
# FIX CRÍTICO — Forzar el backend PostGIS en producción.
# Sin esto, DATABASE_URL con scheme postgis:// no se traduce al engine GIS
# y las consultas espaciales fallan con:
#   AttributeError: 'DatabaseOperations' object has no attribute 'select'
# ---------------------------------------------------------------------------
DATABASES["default"]["ENGINE"] = "django.contrib.gis.db.backends.postgis"
