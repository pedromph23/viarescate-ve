from __future__ import annotations

import uuid
from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import AuditLog, Inventario, Mision, MovimientoInventario
from .routing.services import RouteService


class AuditService:
    """Servicio centralizado para registrar acciones operativas."""

    RESULTADO_EXITO = AuditLog.Resultados.EXITO
    RESULTADO_ERROR = AuditLog.Resultados.ERROR
    RESULTADO_RECHAZADO = AuditLog.Resultados.RECHAZADO

    @staticmethod
    def get_client_ip(request) -> str | None:
        if request is None:
            return None

        remote_addr = request.META.get("REMOTE_ADDR")

        from django.conf import settings

        if getattr(settings, "AUDIT_TRUST_PROXY_HEADERS", False):
            forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

            if forwarded_for:
                first_ip = forwarded_for.split(",")[0].strip()

                if first_ip:
                    return first_ip

        return remote_addr

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

        objeto_tipo = objeto_tipo or "N/A"
        objeto_id = objeto_id or "N/A"

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


class MissionService:
    """Reglas de negocio para misiones operativas."""

    @staticmethod
    def generate_code() -> str:
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
        suffix = uuid.uuid4().hex[:6].upper()
        return f"MIS-{timestamp}-{suffix}"

    @classmethod
    def prepare_for_create(cls, mission: Mision) -> Mision:
        if not mission.codigo:
            mission.codigo = cls.generate_code()

        mission.full_clean()
        return mission

    @classmethod
    def plan_route(
        cls,
        mission: Mision,
        *,
        save: bool = True,
    ):
        """Calcula y, opcionalmente, persiste la ruta de una misión."""
        return RouteService().calculate_for_mission(
            mission,
            save=save,
        )


class InventoryService:
    """Operaciones transaccionales sobre inventario."""

    @classmethod
    @transaction.atomic
    def register_movement(
        cls,
        *,
        inventario_id,
        tipo: str,
        cantidad,
        usuario=None,
        referencia: str = "",
        observaciones: str = "",
    ) -> MovimientoInventario:
        inventario = (
            Inventario.objects
            .select_for_update()
            .select_related("centro", "recurso")
            .get(pk=inventario_id)
        )

        if cantidad < 0:
            raise ValidationError(
                {"cantidad": "La cantidad no puede ser negativa."}
            )

        if tipo == MovimientoInventario.Tipos.ENTRADA:
            nueva_cantidad = inventario.cantidad + cantidad

        elif tipo == MovimientoInventario.Tipos.SALIDA:
            nueva_cantidad = inventario.cantidad - cantidad

            if nueva_cantidad < 0:
                raise ValidationError(
                    {
                        "cantidad": (
                            "La salida no puede superar la cantidad "
                            "disponible en inventario."
                        )
                    }
                )

        elif tipo == MovimientoInventario.Tipos.AJUSTE:
            nueva_cantidad = cantidad

        else:
            raise ValidationError(
                {"tipo": "Tipo de movimiento de inventario no válido."}
            )

        movimiento = MovimientoInventario(
            inventario=inventario,
            tipo=tipo,
            cantidad=cantidad,
            referencia=referencia,
            observaciones=observaciones,
            realizado_por=usuario,
        )

        movimiento.full_clean()

        inventario.cantidad = nueva_cantidad
        inventario.full_clean()
        inventario.save(update_fields=("cantidad", "actualizado_en"))

        movimiento.save()

        return movimiento
