from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from .models import (
    AuditLog,
    CentroAyuda,
    Inventario,
    Mision,
    MovimientoInventario,
    Recurso,
    ReporteVial,
    Refugio,
    Vehiculo,
    Via,
)


@admin.register(CentroAyuda)
class CentroAyudaAdmin(GISModelAdmin):
    list_display = (
        "nombre",
        "tipo",
        "estado",
        "municipio",
        "parroquia",
        "capacidad",
        "activo",
        "creado_en",
    )
    list_filter = (
        "tipo",
        "activo",
        "estado",
        "municipio",
    )
    search_fields = (
        "nombre",
        "direccion",
        "telefono",
        "estado__nombre",
        "municipio__nombre",
        "parroquia__nombre",
    )
    autocomplete_fields = (
        "estado",
        "municipio",
        "parroquia",
    )
    readonly_fields = (
        "creado_en",
        "actualizado_en",
    )
    fieldsets = (
        (
            "Identificación",
            {
                "fields": (
                    "nombre",
                    "tipo",
                    "activo",
                )
            },
        ),
        (
            "Ubicación territorial",
            {
                "fields": (
                    "estado",
                    "municipio",
                    "parroquia",
                    "ubicacion",
                    "direccion",
                )
            },
        ),
        (
            "Contacto y capacidad",
            {
                "fields": (
                    "telefono",
                    "capacidad",
                )
            },
        ),
        (
            "Información adicional",
            {
                "fields": (
                    "observaciones",
                    "creado_en",
                    "actualizado_en",
                )
            },
        ),
    )
    ordering = ("nombre",)
    list_per_page = 25
    save_on_top = True

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "estado",
            "municipio",
            "parroquia",
        )


@admin.register(Refugio)
class RefugioAdmin(GISModelAdmin):
    list_display = (
        "nombre",
        "estado_operativo",
        "ocupacion_actual",
        "capacidad",
        "porcentaje_ocupacion",
        "estado",
        "municipio",
        "activo",
    )
    list_filter = (
        "estado_operativo",
        "activo",
        "estado",
        "municipio",
    )
    search_fields = (
        "nombre",
        "direccion",
        "telefono",
        "estado__nombre",
        "municipio__nombre",
        "parroquia__nombre",
    )
    autocomplete_fields = (
        "estado",
        "municipio",
        "parroquia",
    )
    readonly_fields = (
        "creado_en",
        "actualizado_en",
    )
    fieldsets = (
        (
            "Identificación",
            {
                "fields": (
                    "nombre",
                    "estado_operativo",
                    "activo",
                )
            },
        ),
        (
            "Ubicación territorial",
            {
                "fields": (
                    "estado",
                    "municipio",
                    "parroquia",
                    "ubicacion",
                    "direccion",
                )
            },
        ),
        (
            "Capacidad y ocupación",
            {
                "fields": (
                    "capacidad",
                    "ocupacion",
                )
            },
        ),
        (
            "Contacto",
            {
                "fields": (
                    "telefono",
                )
            },
        ),
        (
            "Información adicional",
            {
                "fields": (
                    "observaciones",
                    "creado_en",
                    "actualizado_en",
                )
            },
        ),
    )
    ordering = ("nombre",)
    list_per_page = 25
    save_on_top = True

    @admin.display(description="Ocupación")
    def ocupacion_actual(self, obj):
        return obj.ocupacion

    @admin.display(description="% ocupación", ordering="ocupacion")
    def porcentaje_ocupacion(self, obj):
        if obj.capacidad <= 0:
            return "0%"
        porcentaje = (obj.ocupacion / obj.capacidad) * 100
        return f"{porcentaje:.1f}%"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "estado",
            "municipio",
            "parroquia",
        )


@admin.register(Via)
class ViaAdmin(GISModelAdmin):
    list_display = (
        "nombre",
        "codigo",
        "estado_vial",
        "velocidad_referencial",
        "activa",
        "estado",
    )
    list_filter = (
        "estado_vial",
        "activa",
        "estado",
    )
    search_fields = (
        "nombre",
        "codigo",
        "estado__nombre",
    )
    autocomplete_fields = (
        "estado",
    )
    readonly_fields = (
        "creado_en",
        "actualizado_en",
    )
    fieldsets = (
        (
            "Identificación",
            {
                "fields": (
                    "nombre",
                    "codigo",
                    "estado",
                    "activa",
                )
            },
        ),
        (
            "Información vial",
            {
                "fields": (
                    "estado_vial",
                    "velocidad_referencial",
                    "geometria",
                )
            },
        ),
        (
            "Observaciones",
            {
                "fields": (
                    "observaciones",
                    "creado_en",
                    "actualizado_en",
                )
            },
        ),
    )
    ordering = ("nombre",)
    list_per_page = 25
    save_on_top = True

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("estado")


@admin.register(ReporteVial)
class ReporteVialAdmin(GISModelAdmin):
    list_display = (
        "titulo",
        "tipo",
        "severidad",
        "estado_reporte",
        "via",
        "reportado_por",
        "reportado_en",
    )
    list_filter = (
        "tipo",
        "estado_reporte",
        "severidad",
        "reportado_en",
    )
    search_fields = (
        "titulo",
        "descripcion",
        "via__nombre",
        "via__codigo",
        "reportado_por__username",
        "reportado_por__email",
    )
    autocomplete_fields = (
        "via",
        "reportado_por",
    )
    readonly_fields = (
        "reportado_en",
        "actualizado_en",
    )
    date_hierarchy = "reportado_en"
    fieldsets = (
        (
            "Reporte",
            {
                "fields": (
                    "tipo",
                    "estado_reporte",
                    "titulo",
                    "descripcion",
                    "severidad",
                )
            },
        ),
        (
            "Ubicación",
            {
                "fields": (
                    "via",
                    "ubicacion",
                )
            },
        ),
        (
            "Seguimiento",
            {
                "fields": (
                    "reportado_por",
                    "reportado_en",
                    "actualizado_en",
                    "resuelto_en",
                )
            },
        ),
    )
    ordering = ("-reportado_en",)
    list_per_page = 30
    save_on_top = True

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "via",
            "reportado_por",
        )


@admin.register(Vehiculo)
class VehiculoAdmin(GISModelAdmin):
    list_display = (
        "placa",
        "tipo",
        "estado_operativo",
        "capacidad_kg",
        "centro",
        "conductor",
        "activo",
    )
    list_filter = (
        "tipo",
        "estado_operativo",
        "activo",
        "centro",
    )
    search_fields = (
        "placa",
        "observaciones",
        "centro__nombre",
        "conductor__username",
        "conductor__first_name",
        "conductor__last_name",
    )
    autocomplete_fields = (
        "centro",
        "conductor",
    )
    readonly_fields = (
        "creado_en",
        "actualizado_en",
    )
    fieldsets = (
        (
            "Identificación",
            {
                "fields": (
                    "placa",
                    "tipo",
                    "activo",
                )
            },
        ),
        (
            "Operación",
            {
                "fields": (
                    "estado_operativo",
                    "capacidad_kg",
                    "centro",
                    "conductor",
                    "ubicacion",
                )
            },
        ),
        (
            "Información adicional",
            {
                "fields": (
                    "observaciones",
                    "creado_en",
                    "actualizado_en",
                )
            },
        ),
    )
    ordering = ("placa",)
    list_per_page = 25
    save_on_top = True

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "centro",
            "conductor",
        )


@admin.register(Mision)
class MisionAdmin(GISModelAdmin):
    list_display = (
        "codigo",
        "nombre",
        "estado_mision",
        "modo_ruta",
        "prioridad",
        "vehiculo",
        "coordinador",
        "planificada_en",
    )
    list_filter = (
        "estado_mision",
        "modo_ruta",
        "prioridad",
        "planificada_en",
    )
    search_fields = (
        "codigo",
        "nombre",
        "descripcion",
        "vehiculo__placa",
        "coordinador__username",
        "coordinador__first_name",
        "coordinador__last_name",
    )
    autocomplete_fields = (
        "vehiculo",
        "coordinador",
    )
    readonly_fields = (
        "planificada_en",
        "iniciada_en",
        "entregada_en",
        "cancelada_en",
    )
    date_hierarchy = "planificada_en"
    list_per_page = 25
    save_on_top = True

    fieldsets = (
        (
            "Identificación",
            {
                "fields": (
                    "codigo",
                    "nombre",
                    "descripcion",
                )
            },
        ),
        (
            "Planificación",
            {
                "fields": (
                    "estado_mision",
                    "modo_ruta",
                    "prioridad",
                    "vehiculo",
                    "coordinador",
                )
            },
        ),
        (
            "Ruta",
            {
                "fields": (
                    "origen",
                    "destino",
                    "ruta",
                    "distancia_km",
                    "tiempo_estimado_minutos",
                )
            },
        ),
        (
            "Seguimiento",
            {
                "fields": (
                    "planificada_en",
                    "iniciada_en",
                    "entregada_en",
                    "cancelada_en",
                    "observaciones",
                )
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "vehiculo",
            "coordinador",
        )


@admin.register(Recurso)
class RecursoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "unidad",
        "activo",
    )
    list_filter = (
        "activo",
    )
    search_fields = (
        "nombre",
        "unidad",
        "descripcion",
    )
    readonly_fields = ()
    ordering = ("nombre",)
    list_per_page = 30


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = (
        "centro",
        "recurso",
        "cantidad",
        "minimo",
        "estado_stock",
        "actualizado_en",
    )
    list_filter = (
        "centro",
        "recurso",
    )
    search_fields = (
        "centro__nombre",
        "recurso__nombre",
    )
    autocomplete_fields = (
        "centro",
        "recurso",
    )
    readonly_fields = (
        "actualizado_en",
    )
    fieldsets = (
        (
            "Existencia",
            {
                "fields": (
                    "centro",
                    "recurso",
                    "cantidad",
                    "minimo",
                )
            },
        ),
        (
            "Actualización",
            {
                "fields": (
                    "actualizado_en",
                )
            },
        ),
    )
    ordering = (
        "centro__nombre",
        "recurso__nombre",
    )
    list_per_page = 30

    @admin.display(description="Estado")
    def estado_stock(self, obj):
        if obj.cantidad <= obj.minimo:
            return "Bajo"
        return "Disponible"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "centro",
            "recurso",
        )


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = (
        "tipo",
        "inventario",
        "cantidad",
        "realizado_por",
        "creado_en",
    )
    list_filter = (
        "tipo",
        "creado_en",
    )
    search_fields = (
        "inventario__centro__nombre",
        "inventario__recurso__nombre",
        "referencia",
        "observaciones",
        "realizado_por__username",
    )
    autocomplete_fields = (
        "inventario",
        "realizado_por",
    )
    readonly_fields = (
        "creado_en",
    )
    date_hierarchy = "creado_en"
    fieldsets = (
        (
            "Movimiento",
            {
                "fields": (
                    "tipo",
                    "inventario",
                    "cantidad",
                    "referencia",
                    "observaciones",
                )
            },
        ),
        (
            "Registro",
            {
                "fields": (
                    "realizado_por",
                    "creado_en",
                )
            },
        ),
    )
    ordering = ("-creado_en",)
    list_per_page = 30

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "inventario__centro",
            "inventario__recurso",
            "realizado_por",
        )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "fecha",
        "usuario",
        "accion",
        "modulo",
        "objeto_tipo",
        "objeto_id",
        "resultado",
        "ip",
    )
    list_filter = (
        "resultado",
        "modulo",
        "accion",
        "fecha",
    )
    search_fields = (
        "accion",
        "modulo",
        "objeto_tipo",
        "objeto_id",
        "usuario__username",
        "usuario__email",
        "ip",
    )
    readonly_fields = (
        "usuario",
        "accion",
        "modulo",
        "objeto_tipo",
        "objeto_id",
        "fecha",
        "ip",
        "detalles",
        "resultado",
    )
    date_hierarchy = "fecha"
    ordering = ("-fecha",)
    list_per_page = 50
    save_on_top = True

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
