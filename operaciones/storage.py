"""Storage personalizado para Supabase Storage."""
import re

from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


def _derivar_public_url(endpoint, bucket):
    """
    Deriva la URL pública desde el endpoint S3 si no está configurada.

    https://xxx.storage.supabase.co/storage/v1/s3
        → https://xxx.supabase.co/storage/v1/object/public/{bucket}/
    """
    if not endpoint:
        return ""
    m = re.match(r"https://([a-z0-9]+)\.storage\.supabase\.co", endpoint)
    if m:
        ref = m.group(1)
        return f"https://{ref}.supabase.co/storage/v1/object/public/{bucket}/"
    return ""


class SupabasePublicStorage(S3Boto3Storage):
    """
    Storage S3 de Supabase con URL pública correcta.

    Sobrescribe `url()` porque S3Boto3Storage por defecto genera URLs
    apuntando al endpoint S3 (storage/v1/s3/media/...) pero Supabase sirve
    los archivos públicos en otro path (object/public/media/...).
    """

    def url(self, name, parameters=None, expire=None, http_method=None):
        public_url = getattr(settings, "SUPABASE_S3_PUBLIC_URL", "") or ""

        # Fallback: derivar desde el endpoint si no está configurado
        if not public_url:
            bucket = getattr(settings, "SUPABASE_S3_BUCKET", "media")
            public_url = _derivar_public_url(self.endpoint_url, bucket)

        base = public_url.rstrip("/")
        return f"{base}/{name.lstrip('/')}"
