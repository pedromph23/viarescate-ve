"""URLs públicas — accesibles sin login, URL limpia /reportar/."""
from django.urls import path

from . import views_publico

app_name = "reportes_publicos"

urlpatterns = [
    path("", views_publico.reportar_publico, name="home"),
    path(
        "gracias/<uuid:pk>/",
        views_publico.reporte_publico_gracias,
        name="gracias",
    ),
]
