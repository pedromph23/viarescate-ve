from django.contrib import admin
from django.http import Http404
from django.urls import include, path


def admin_404(request):
    """Devuelve 404 en /admin/ para no revelar la ruta real."""
    raise Http404()


urlpatterns = [
    path("", include("core.urls")),
    path("admin/", admin_404),  # <-- bloquea /admin/ clásico
    path("panel-django/", admin.site.urls),  # <-- admin real (URL discreta)
    path("administracion/", include("panel.urls")),
    path("usuarios/", include("usuarios.urls")),
    path("api/", include("operaciones.api.urls")),
    path("mapa/", include("mapa.urls")),
    path("operaciones/", include("operaciones.urls")),
]
