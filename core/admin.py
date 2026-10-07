from django.contrib import admin

from .models import Estado, Municipio, Parroquia


@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre")
    search_fields = ("codigo", "nombre")
    ordering = ("nombre",)


@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "estado")
    list_filter = ("estado",)
    search_fields = ("nombre", "estado__nombre")
    ordering = ("estado__nombre", "nombre")


@admin.register(Parroquia)
class ParroquiaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "municipio", "estado")
    list_filter = ("municipio__estado", "municipio")
    search_fields = (
        "nombre",
        "municipio__nombre",
        "municipio__estado__nombre",
    )
    ordering = (
        "municipio__estado__nombre",
        "municipio__nombre",
        "nombre",
    )

    @admin.display(description="Estado")
    def estado(self, obj):
        return obj.municipio.estado
