from django.urls import path

from . import views

app_name = "mapa"

urlpatterns = [
    path("", views.mapa_publico, name="publico"),
    path(
        "api/geojson/centros-ayuda/",
        views.centros_ayuda_geojson_view,
        name="geojson-centros-ayuda",
    ),
    path(
        "api/geojson/refugios/",
        views.refugios_geojson_view,
        name="geojson-refugios",
    ),
    path(
        "api/geojson/vias/",
        views.vias_geojson_view,
        name="geojson-vias",
    ),
    path(
        "api/geojson/reportes-viales/",
        views.reportes_viales_geojson_view,
        name="geojson-reportes-viales",
    ),
]


# Capas operativas protegidas: requieren autenticación.
urlpatterns += [
    path(
        "api/geojson/vehiculos/",
        views.vehiculos_geojson_view,
        name="geojson-vehiculos",
    ),
    path(
        "api/geojson/misiones/",
        views.misiones_geojson_view,
        name="geojson-misiones",
    ),
]
