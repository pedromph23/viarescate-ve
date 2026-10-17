from django.urls import path

from . import views, views_publico

app_name = "operaciones"

urlpatterns = [
    path("", views.centro_operativo, name="centro"),
    # Reportes públicos
    path("reportar/", views_publico.reportar_publico, name="reporte_publico"),
    path(
        "reportar/gracias/<uuid:pk>/",
        views_publico.reporte_publico_gracias,
        name="reporte_publico_gracias",
    ),
]
