from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .permissions import puede_acceder_panel, tiene_permiso


def panel_required(view_func):
    """Requiere login + al menos un permiso del panel."""
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if puede_acceder_panel(request.user):
            return view_func(request, *args, **kwargs)
        raise PermissionDenied("No tiene permisos para acceder al panel.")
    return _wrapped


def permiso_requerido(permiso):
    """
    Requiere un permiso específico (ej: 'crear_centros').
    Uso: @permiso_requerido("editar_refugios")
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if tiene_permiso(request.user, permiso):
                return view_func(request, *args, **kwargs)
            raise PermissionDenied(
                f"No tiene permiso '{permiso}' para esta acción."
            )
        return _wrapped
    return decorator


def puede_usar_panel(user):
    """Compatibilidad con código existente."""
    return puede_acceder_panel(user)
