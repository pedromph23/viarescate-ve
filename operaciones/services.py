from __future__ import annotations

from typing import Any


from .models import AuditLog


class AuditService:
    """Servicio centralizado para registrar acciones operativas."""

    RESULTADO_EXITO = AuditLog.Resultados.EXITO
    RESULTADO_ERROR = AuditLog.Resultados.ERROR
    RESULTADO_RECHAZADO = AuditLog.Resultados.RECHAZADO

    @staticmethod
    def get_client_ip(request) -> str | None:
        if request is None:
            return None

        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip() or None

        return request.META.get("REMOTE_ADDR")

    @classmethod
    def log(
        cls,
        *,
        request=None,
        accion: str,
        modulo: str,
        objeto=None,
        objeto_tipo: str | None = None,
        objeto_id: str | None = None,
        detalles: dict[str, Any] | None = None,
        resultado: str = RESULTADO_EXITO,
    ) -> AuditLog:
        usuario = None

        if request is not None:
            request_user = getattr(request, "user", None)
            if (
                request_user is not None
                and getattr(request_user, "is_authenticated", False)
            ):
                usuario = request_user

        if objeto is not None:
            objeto_tipo = objeto_tipo or objeto.__class__.__name__
            objeto_id = objeto_id or str(objeto.pk)

        if not objeto_tipo:
            objeto_tipo = "N/A"

        if not objeto_id:
            objeto_id = "N/A"

        return AuditLog.objects.create(
            usuario=usuario,
            accion=accion,
            modulo=modulo,
            objeto_tipo=objeto_tipo,
            objeto_id=objeto_id,
            ip=cls.get_client_ip(request),
            detalles=detalles or {},
            resultado=resultado,
        )
