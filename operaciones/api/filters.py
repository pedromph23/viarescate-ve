import django_filters
from django.db.models import F

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


class CentroAyudaFilter(django_filters.FilterSet):
    activo = django_filters.BooleanFilter()
    tipo = django_filters.CharFilter()
    estado = django_filters.UUIDFilter(field_name="estado_id")
    municipio = django_filters.UUIDFilter(field_name="municipio_id")
    parroquia = django_filters.UUIDFilter(field_name="parroquia_id")

    class Meta:
        model = CentroAyuda
        fields = ("activo", "tipo", "estado", "municipio", "parroquia")


class RefugioFilter(django_filters.FilterSet):
    activo = django_filters.BooleanFilter()
    estado_operativo = django_filters.CharFilter()
    estado = django_filters.UUIDFilter(field_name="estado_id")
    municipio = django_filters.UUIDFilter(field_name="municipio_id")
    parroquia = django_filters.UUIDFilter(field_name="parroquia_id")

    class Meta:
        model = Refugio
        fields = (
            "activo",
            "estado_operativo",
            "estado",
            "municipio",
            "parroquia",
        )


class ViaFilter(django_filters.FilterSet):
    activa = django_filters.BooleanFilter()
    estado_vial = django_filters.CharFilter()
    estado = django_filters.UUIDFilter(field_name="estado_id")

    class Meta:
        model = Via
        fields = ("activa", "estado_vial", "estado")


class ReporteVialFilter(django_filters.FilterSet):
    tipo = django_filters.CharFilter()
    estado_reporte = django_filters.CharFilter()
    severidad = django_filters.NumberFilter()
    severidad_min = django_filters.NumberFilter(
        field_name="severidad",
        lookup_expr="gte",
    )
    severidad_max = django_filters.NumberFilter(
        field_name="severidad",
        lookup_expr="lte",
    )
    via = django_filters.UUIDFilter(field_name="via_id")

    class Meta:
        model = ReporteVial
        fields = (
            "tipo",
            "estado_reporte",
            "severidad",
            "severidad_min",
            "severidad_max",
            "via",
        )


class VehiculoFilter(django_filters.FilterSet):
    tipo = django_filters.CharFilter()
    estado_operativo = django_filters.CharFilter()
    activo = django_filters.BooleanFilter()
    centro = django_filters.UUIDFilter(field_name="centro_id")
    conductor = django_filters.UUIDFilter(field_name="conductor_id")

    class Meta:
        model = Vehiculo
        fields = (
            "tipo",
            "estado_operativo",
            "activo",
            "centro",
            "conductor",
        )


class MisionFilter(django_filters.FilterSet):
    estado_mision = django_filters.CharFilter()
    modo_ruta = django_filters.CharFilter()
    prioridad = django_filters.NumberFilter()
    prioridad_min = django_filters.NumberFilter(
        field_name="prioridad",
        lookup_expr="gte",
    )
    prioridad_max = django_filters.NumberFilter(
        field_name="prioridad",
        lookup_expr="lte",
    )
    vehiculo = django_filters.UUIDFilter(field_name="vehiculo_id")
    coordinador = django_filters.UUIDFilter(field_name="coordinador_id")

    class Meta:
        model = Mision
        fields = (
            "estado_mision",
            "modo_ruta",
            "prioridad",
            "prioridad_min",
            "prioridad_max",
            "vehiculo",
            "coordinador",
        )


class RecursoFilter(django_filters.FilterSet):
    activo = django_filters.BooleanFilter()

    class Meta:
        model = Recurso
        fields = ("activo",)


class InventarioFilter(django_filters.FilterSet):
    centro = django_filters.UUIDFilter(field_name="centro_id")
    recurso = django_filters.UUIDFilter(field_name="recurso_id")
    cantidad_min = django_filters.NumberFilter(
        field_name="cantidad",
        lookup_expr="gte",
    )
    cantidad_max = django_filters.NumberFilter(
        field_name="cantidad",
        lookup_expr="lte",
    )
    bajo_minimo = django_filters.BooleanFilter(
        method="filter_bajo_minimo",
    )

    class Meta:
        model = Inventario
        fields = (
            "centro",
            "recurso",
            "cantidad_min",
            "cantidad_max",
            "bajo_minimo",
        )

    def filter_bajo_minimo(self, queryset, name, value):
        if value:
            return queryset.filter(cantidad__lte=F("minimo"))

        if value is False:
            return queryset.filter(cantidad__gt=F("minimo"))

        return queryset


class MovimientoInventarioFilter(django_filters.FilterSet):
    tipo = django_filters.CharFilter()
    inventario = django_filters.UUIDFilter(field_name="inventario_id")
    realizado_por = django_filters.UUIDFilter(field_name="realizado_por_id")

    class Meta:
        model = MovimientoInventario
        fields = ("tipo", "inventario", "realizado_por")


class AuditLogFilter(django_filters.FilterSet):
    usuario = django_filters.UUIDFilter(field_name="usuario_id")
    accion = django_filters.CharFilter()
    modulo = django_filters.CharFilter()
    resultado = django_filters.CharFilter()
    objeto_tipo = django_filters.CharFilter()
    objeto_id = django_filters.CharFilter()

    class Meta:
        model = AuditLog
        fields = (
            "usuario",
            "accion",
            "modulo",
            "resultado",
            "objeto_tipo",
            "objeto_id",
        )
