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
    path("usuarios/<uuid:pk>/toggle/", views.usuarios_toggle, name="usuarios_toggle"),
    path("vias/", views.vias_lista, name="vias_lista"),
    path("reportes/", views.reportes_lista, name="reportes_lista"),
    path("necesidades/", views.necesidades_lista, name="necesidades_lista"),
    path("necesidades/nueva/", views.necesidades_form, name="necesidades_nueva"),
    path("necesidades/<uuid:pk>/editar/", views.necesidades_form, name="necesidades_editar"),
    path("necesidades/<uuid:pk>/eliminar/", views.necesidades_eliminar, name="necesidades_eliminar"),
]
