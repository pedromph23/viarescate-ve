"""
Configuración para desarrollo local.
"""

from .base import *  # noqa: F403,F401


DEBUG = True

ALLOWED_HOSTS = env.list(
    "DJANGO_ALLOWED_HOSTS",
    default=["127.0.0.1", "localhost"],
)
