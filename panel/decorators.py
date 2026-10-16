from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

ROLES_PANEL = ("ADMINISTRADOR", "COORDINADOR")


def panel_required(view_func):
    """Permite acceso solo a is_staff o rol ADMINISTRADOR/COORDINADOR."""

    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        user = request.user
        if user.is_staff or user.is_superuser or user.rol in ROLES_PANEL:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied("No tiene permisos para acceder al panel.")

    return _wrapped


def puede_usar_panel(user):
    if not user.is_authenticated:
        return False
    return bool(
        user.is_staff or user.is_superuser or user.rol in ROLES_PANEL
    )
