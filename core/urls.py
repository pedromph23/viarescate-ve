from django.urls import path

from . import api_views, views

app_name = "core"

urlpatterns = [
    path("", views.inicio_publico, name="inicio"),
    path("health/", views.health, name="health"),
    # Cascading selects (JSON)
    path(
        "api/municipios/<int:estado_id>/",
        api_views.municipios_por_estado,
        name="municipios_por_estado",
    ),
    path(
        "api/parroquias/<int:municipio_id>/",
        api_views.parroquias_por_municipio,
        name="parroquias_por_municipio",
    ),
]
