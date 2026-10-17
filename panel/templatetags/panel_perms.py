"""Template tags para verificar permisos desde templates."""
from django import template

from panel.permissions import tiene_permiso as _tiene_permiso

register = template.Library()


@register.simple_tag(takes_context=True)
def if_permiso(context, permiso):
    """Devuelve True si el usuario tiene el permiso."""
    user = context.get("user")
    if not user:
        return False
    return _tiene_permiso(user, permiso)


@register.simple_tag(takes_context=True)
def tiene_algún_permiso(context, *permisos):
    """Devuelve True si el usuario tiene AL MENOS UNO de los permisos."""
    user = context.get("user")
    if not user:
        return False
    return any(_tiene_permiso(user, p) for p in permisos)
