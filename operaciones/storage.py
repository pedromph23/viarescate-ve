"""Storage personalizado para Supabase Storage."""
import logging
import os
import re
import uuid

from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

logger = logging.getLogger(__name__)


def _derivar_public_url(endpoint, bucket):
    if not endpoint:
        return ""
    m = re.match(r"https://([a-z0-9]+)\.storage\.supabase\.co", endpoint)
    if m:
        ref = m.group(1)
        return f"https://{ref}.supabase.co/storage/v1/object/public/{bucket}/"
    return ""


class SupabasePublicStorage(S3Boto3Storage):
    """
    Storage S3 de Supabase con:
    - URL pública correcta (object/public/media/)
    - get_available_name() que NO llama a exists()/HeadObject (evita 403)
    """

    def get_available_name(self, name, max_length=None):
        """
        Genera un nombre único con UUID sin hacer HeadObject.
        Evita el error 403 que rompe el POST cuando las credenciales
        S3 no tienen permiso GetObject.
        """
        base, ext = os.path.splitext(name)
        unique = uuid.uuid4().hex[:8]
        return f"{base}_{unique}{ext}"

    def url(self, name, parameters=None, expire=None, http_method=None):
        try:
            public_url = getattr(settings, "SUPABASE_S3_PUBLIC_URL", "") or ""
            if not public_url:
                bucket = getattr(settings, "SUPABASE_S3_BUCKET", "media")
                public_url = _derivar_public_url(self.endpoint_url, bucket)
            if not public_url:
                return super().url(
                    name, parameters=parameters, expire=expire,
                    http_method=http_method,
                )
            base = public_url.rstrip("/")
            return f"{base}/{name.lstrip('/')}"
        except Exception as exc:
            logger.warning("Error construyendo URL de Storage: %s", exc)
            return f"/media/{name.lstrip('/')}"
