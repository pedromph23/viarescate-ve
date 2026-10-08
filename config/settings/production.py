"""
Configuración de producción de VíaRescate VE.

Todos los valores sensibles y dependientes del entorno se obtienen
desde variables de entorno.
"""

from .base import *  # noqa: F403,F401


DEBUG = False


ALLOWED_HOSTS = env.list(
    "DJANGO_ALLOWED_HOSTS",
    default=[],
)

CSRF_TRUSTED_ORIGINS = env.list(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    default=[],
)


# Render y otros proxies/reverse proxies terminan TLS antes de
# entregar la petición a Django.
SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)

SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"


# La clave debe ser obligatoria en producción.
SECRET_KEY = env("DJANGO_SECRET_KEY")


# La aplicación detrás de un proxy confiable puede utilizar
# X-Forwarded-For para registrar la IP original del cliente.
AUDIT_TRUST_PROXY_HEADERS = env.bool(
    "AUDIT_TRUST_PROXY_HEADERS",
    default=True,
)
