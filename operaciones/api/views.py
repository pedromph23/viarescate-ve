from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from rest_framework import filters, serializers, status, viewsets
from rest_framework.response import Response

from operaciones.models import (
    AuditLog,
    CentroAyuda,
    Inventario,
    Mision,
    MovimientoInventario,
    Recurso,
    Refugio,
    ReporteVial,
    Vehiculo,
    Via,
)
from operaciones.services import AuditService, InventoryService

from .filters import (
    AuditLogFilter,
    CentroAyudaFilter,
    InventarioFilter,
    MisionFilter,
    MovimientoInventarioFilter,
    RecursoFilter,
    RefugioFilter,
    ReporteVialFilter,
    VehiculoFilter,
    ViaFilter,
)
from .permissions import (
    AuditLogPermission,
    IsAdministrador,
    IsAuthenticatedRole,
    IsCoordinadorOrAdmin,
    IsOperadorOrAbove,
    IsVoluntarioOrAbove,
    ReadOnlyOrAuthenticatedRole,
)
from .serializers import (
    AuditLogSerializer,
    CentroAyudaSerializer,
    InventarioSerializer,
    MisionSerializer,
    MovimientoInventarioSerializer,
    RecursoSerializer,
    RefugioSerializer,
    ReporteVialSerializer,
    VehiculoSerializer,
    ViaSerializer,
)


class AuditableModelViewSet(viewsets.ModelViewSet):
    """
    ViewSet base para operaciones auditables.
    """

    def get_permissions(self):
        permission_classes = self.permission_classes

        if isinstance(permission_classes, dict):
            permission_class = permission_classes.get(
                self.action,
                ReadOnlyOrAuthenticatedRole,
            )
            return [permission_class()]

        return super().get_permissions()

    def _audit(
        self,
        accion,
        instance=None,
        *,
        objeto_tipo=None,
        objeto_id=None,
        detalles=None,
        resultado=AuditService.RESULTADO_EXITO,
    ):
        AuditService.log(
            request=self.request,
            accion=accion,
            modulo="operaciones",
            objeto=instance,
            objeto_tipo=objeto_tipo,
            objeto_id=objeto_id,
            detalles=detalles,
            resultado=resultado,
        )

    def perform_create(self, serializer):
        with transaction.atomic():
            instance = serializer.save()
            self._audit("CREAR", instance)

    def perform_update(self, serializer):
        with transaction.atomic():
            instance = serializer.save()
            self._audit("ACTUALIZAR", instance)

    def perform_destroy(self, instance):
        object_type = instance.__class__.__name__
        object_id = str(instance.pk)

        with transaction.atomic():
            instance.delete()

            self._audit(
                "ELIMINAR",
                objeto_tipo=object_type,
                objeto_id=object_id,
            )


class CentroAyudaViewSet(AuditableModelViewSet):
    queryset = CentroAyuda.objects.select_related(
        "estado",
        "municipio",
        "parroquia",
    )
    serializer_class = CentroAyudaSerializer
    filterset_class = CentroAyudaFilter

    search_fields = (
        "nombre",
        "direccion",
        "telefono",
        "observaciones",
        "estado__nombre",
        "municipio__nombre",
        "parroquia__nombre",
    )

    ordering_fields = (
        "nombre",
        "tipo",
        "capacidad",
        "activo",
        "creado_en",
        "actualizado_en",
    )

    ordering = ("nombre",)

    permission_classes = {
        "list": ReadOnlyOrAuthenticatedRole,
        "retrieve": ReadOnlyOrAuthenticatedRole,
        "create": IsCoordinadorOrAdmin,
        "update": IsCoordinadorOrAdmin,
        "partial_update": IsCoordinadorOrAdmin,
        "destroy": IsAdministrador,
    }


class RefugioViewSet(AuditableModelViewSet):
    queryset = Refugio.objects.select_related(
        "estado",
        "municipio",
        "parroquia",
    )
    serializer_class = RefugioSerializer
    filterset_class = RefugioFilter

    search_fields = (
        "nombre",
        "direccion",
        "telefono",
        "observaciones",
        "estado__nombre",
        "municipio__nombre",
        "parroquia__nombre",
    )

    ordering_fields = (
        "nombre",
        "capacidad",
        "ocupacion",
        "estado_operativo",
        "activo",
        "creado_en",
        "actualizado_en",
    )

    ordering = ("nombre",)

    permission_classes = {
        "list": ReadOnlyOrAuthenticatedRole,
        "retrieve": ReadOnlyOrAuthenticatedRole,
        "create": IsCoordinadorOrAdmin,
        "update": IsCoordinadorOrAdmin,
        "partial_update": IsCoordinadorOrAdmin,
        "destroy": IsAdministrador,
    }


class ViaViewSet(AuditableModelViewSet):
    queryset = Via.objects.select_related("estado")
    serializer_class = ViaSerializer
    filterset_class = ViaFilter

    search_fields = (
        "nombre",
        "codigo",
        "observaciones",
        "estado__nombre",
    )

    ordering_fields = (
        "nombre",
        "codigo",
        "estado_vial",
        "velocidad_referencial",
        "activa",
        "creado_en",
        "actualizado_en",
    )

    ordering = ("nombre",)

    permission_classes = {
        "list": ReadOnlyOrAuthenticatedRole,
        "retrieve": ReadOnlyOrAuthenticatedRole,
        "create": IsCoordinadorOrAdmin,
        "update": IsCoordinadorOrAdmin,
        "partial_update": IsCoordinadorOrAdmin,
        "destroy": IsAdministrador,
    }


class ReporteVialViewSet(AuditableModelViewSet):
    queryset = ReporteVial.objects.select_related(
        "via",
        "reportado_por",
    )
    serializer_class = ReporteVialSerializer
    filterset_class = ReporteVialFilter

    search_fields = (
        "titulo",
        "descripcion",
        "via__nombre",
        "reportado_por__username",
        "reportado_por__first_name",
        "reportado_por__last_name",
    )

    ordering_fields = (
        "reportado_en",
        "actualizado_en",
        "severidad",
        "tipo",
        "estado_reporte",
    )

    ordering = ("-reportado_en",)

    permission_classes = {
        "list": ReadOnlyOrAuthenticatedRole,
        "retrieve": ReadOnlyOrAuthenticatedRole,
        "create": IsVoluntarioOrAbove,
        "update": IsOperadorOrAbove,
        "partial_update": IsOperadorOrAbove,
        "destroy": IsAdministrador,
    }

    def perform_create(self, serializer):
        with transaction.atomic():
            instance = serializer.save(
                reportado_por=self.request.user
            )
            self._audit("CREAR_REPORTE_VIAL", instance)

    def perform_update(self, serializer):
        previous_state = serializer.instance.estado_reporte

        with transaction.atomic():
            instance = serializer.save()

            if (
                instance.estado_reporte == ReporteVial.Estados.RESUELTO
                and previous_state != ReporteVial.Estados.RESUELTO
                and instance.resuelto_en is None
            ):
                instance.resuelto_en = timezone.now()
                instance.save(
                    update_fields=(
                        "resuelto_en",
                        "actualizado_en",
                    )
                )

            self._audit(
                "ACTUALIZAR_REPORTE_VIAL",
                instance,
            )


class VehiculoViewSet(AuditableModelViewSet):
    queryset = Vehiculo.objects.select_related(
        "centro",
        "conductor",
    )
    serializer_class = VehiculoSerializer
    filterset_class = VehiculoFilter

    search_fields = (
        "placa",
        "observaciones",
        "centro__nombre",
        "conductor__username",
        "conductor__first_name",
        "conductor__last_name",
    )

    ordering_fields = (
        "placa",
        "tipo",
        "estado_operativo",
        "capacidad_kg",
        "activo",
        "creado_en",
        "actualizado_en",
    )

    ordering = ("placa",)

    permission_classes = {
        "list": IsAuthenticatedRole,
        "retrieve": IsAuthenticatedRole,
        "create": IsCoordinadorOrAdmin,
        "update": IsCoordinadorOrAdmin,
        "partial_update": IsCoordinadorOrAdmin,
        "destroy": IsAdministrador,
    }


class MisionViewSet(AuditableModelViewSet):
    queryset = Mision.objects.select_related(
        "vehiculo",
        "coordinador",
    )
    serializer_class = MisionSerializer
    filterset_class = MisionFilter

    search_fields = (
        "codigo",
        "nombre",
        "descripcion",
        "observaciones",
        "vehiculo__placa",
        "coordinador__username",
        "coordinador__first_name",
        "coordinador__last_name",
    )

    ordering_fields = (
        "planificada_en",
        "estado_mision",
        "modo_ruta",
        "prioridad",
        "distancia_km",
        "tiempo_estimado_minutos",
    )

    ordering = ("-planificada_en",)

    permission_classes = {
        "list": IsAuthenticatedRole,
        "retrieve": IsAuthenticatedRole,
        "create": IsCoordinadorOrAdmin,
        "update": IsCoordinadorOrAdmin,
        "partial_update": IsCoordinadorOrAdmin,
        "destroy": IsAdministrador,
    }

    def perform_create(self, serializer):
        with transaction.atomic():
            instance = serializer.save()
            self._audit("CREAR_MISION", instance)


class RecursoViewSet(AuditableModelViewSet):
    queryset = Recurso.objects.all()
    serializer_class = RecursoSerializer
    filterset_class = RecursoFilter

    search_fields = (
        "nombre",
        "unidad",
        "descripcion",
    )

    ordering_fields = (
        "nombre",
        "unidad",
        "activo",
    )

    ordering = ("nombre",)

    permission_classes = {
        "list": ReadOnlyOrAuthenticatedRole,
        "retrieve": ReadOnlyOrAuthenticatedRole,
        "create": IsCoordinadorOrAdmin,
        "update": IsCoordinadorOrAdmin,
        "partial_update": IsCoordinadorOrAdmin,
        "destroy": IsAdministrador,
    }


class InventarioViewSet(AuditableModelViewSet):
    queryset = Inventario.objects.select_related(
        "centro",
        "recurso",
    )
    serializer_class = InventarioSerializer
    filterset_class = InventarioFilter

    search_fields = (
        "centro__nombre",
        "recurso__nombre",
        "recurso__unidad",
    )

    ordering_fields = (
        "cantidad",
        "minimo",
        "actualizado_en",
        "centro__nombre",
        "recurso__nombre",
    )

    ordering = (
        "centro__nombre",
        "recurso__nombre",
    )

    permission_classes = {
        "list": IsAuthenticatedRole,
        "retrieve": IsAuthenticatedRole,
        "create": IsOperadorOrAbove,
        "update": IsOperadorOrAbove,
        "partial_update": IsOperadorOrAbove,
        "destroy": IsAdministrador,
    }


class MovimientoInventarioViewSet(AuditableModelViewSet):
    queryset = MovimientoInventario.objects.select_related(
        "inventario__centro",
        "inventario__recurso",
        "realizado_por",
    )

    serializer_class = MovimientoInventarioSerializer
    filterset_class = MovimientoInventarioFilter

    search_fields = (
        "referencia",
        "observaciones",
        "inventario__centro__nombre",
        "inventario__recurso__nombre",
        "realizado_por__username",
    )

    ordering_fields = (
        "creado_en",
        "cantidad",
        "tipo",
    )

    ordering = ("-creado_en",)

    permission_classes = {
        "list": IsAuthenticatedRole,
        "retrieve": IsAuthenticatedRole,
        "create": IsOperadorOrAbove,
        "update": IsOperadorOrAbove,
        "partial_update": IsOperadorOrAbove,
        "destroy": IsAdministrador,
    }

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                movimiento = InventoryService.register_movement(
                    inventario_id=serializer.validated_data["inventario"].pk,
                    tipo=serializer.validated_data["tipo"],
                    cantidad=serializer.validated_data["cantidad"],
                    usuario=request.user,
                    referencia=serializer.validated_data.get(
                        "referencia",
                        "",
                    ),
                    observaciones=serializer.validated_data.get(
                        "observaciones",
                        "",
                    ),
                )

                self._audit(
                    "CREAR_MOVIMIENTO_INVENTARIO",
                    movimiento,
                )

        except ValidationError as exc:
            raise serializers.ValidationError(exc.message_dict)

        output = self.get_serializer(movimiento)

        return Response(
            output.data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        return Response(
            {
                "detail": (
                    "Los movimientos de inventario son inmutables "
                    "y no pueden ser modificados."
                )
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def partial_update(self, request, *args, **kwargs):
        return Response(
            {
                "detail": (
                    "Los movimientos de inventario son inmutables "
                    "y no pueden ser modificados."
                )
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def destroy(self, request, *args, **kwargs):
        return Response(
            {
                "detail": (
                    "Los movimientos de inventario son inmutables "
                    "y no pueden ser eliminados."
                )
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.select_related("usuario")
    serializer_class = AuditLogSerializer
    filterset_class = AuditLogFilter
    permission_classes = (AuditLogPermission,)

    search_fields = (
        "accion",
        "modulo",
        "objeto_tipo",
        "objeto_id",
        "usuario__username",
        "usuario__email",
        "ip",
    )

    ordering_fields = (
        "fecha",
        "accion",
        "modulo",
        "resultado",
    )

    ordering = ("-fecha",)
