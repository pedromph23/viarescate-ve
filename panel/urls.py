from django.urls import path

from . import views

app_name = "panel"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("centros/", views.centros_lista, name="centros_lista"),
    path("centros/nuevo/", views.centros_form, name="centros_nuevo"),
    path("centros/<uuid:pk>/editar/", views.centros_form, name="centros_editar"),
    path("centros/<uuid:pk>/eliminar/", views.centros_eliminar, name="centros_eliminar"),
    path("refugios/", views.refugios_lista, name="refugios_lista"),
    path("refugios/nuevo/", views.refugios_form, name="refugios_nuevo"),
    path("refugios/<uuid:pk>/editar/", views.refugios_form, name="refugios_editar"),
    path("refugios/<uuid:pk>/eliminar/", views.refugios_eliminar, name="refugios_eliminar"),
    path("usuarios/", views.usuarios_lista, name="usuarios_lista"),
    path("usuarios/nuevo/", views.usuarios_form, name="usuarios_nuevo"),
    path("usuarios/<uuid:pk>/editar/", views.usuarios_form, name="usuarios_editar"),
    path("usuarios/<uuid:pk>/toggle/", views.usuarios_toggle, name="usuarios_toggle"),
    path("usuarios/<uuid:pk>/eliminar/", views.usuarios_eliminar, name="usuarios_eliminar"),
    path("vias/", views.vias_lista, name="vias_lista"),
    path("vias/nueva/", views.vias_form, name="vias_nueva"),
    path("vias/<uuid:pk>/editar/", views.vias_form, name="vias_editar"),
    path("vias/<uuid:pk>/eliminar/", views.vias_eliminar, name="vias_eliminar"),
    path("reportes/", views.reportes_lista, name="reportes_lista"),
    path("reportes/nuevo/", views.reportes_form, name="reportes_nuevo"),
    path("reportes/<uuid:pk>/editar/", views.reportes_form, name="reportes_editar"),
    path("reportes/<uuid:pk>/eliminar/", views.reportes_eliminar, name="reportes_eliminar"),
    path("necesidades/", views.necesidades_lista, name="necesidades_lista"),
    path("necesidades/nueva/", views.necesidades_form, name="necesidades_nueva"),
    path("necesidades/<uuid:pk>/editar/", views.necesidades_form, name="necesidades_editar"),
    path("necesidades/<uuid:pk>/eliminar/", views.necesidades_eliminar, name="necesidades_eliminar"),
    # IA / Predicciones
    path("alertas/", views.alertas_lista, name="alertas_lista"),
    path("alertas/<uuid:pk>/reconocer/", views.alertas_reconocer, name="alertas_reconocer"),
    path("predicciones/demanda/", views.predicciones_demanda, name="predicciones_demanda"),
    path("predicciones/misiones/", views.predicciones_misiones, name="predicciones_misiones"),
]
