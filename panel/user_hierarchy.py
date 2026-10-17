"""
Jerarquía y reglas de gestión de usuarios — VíaRescate VE.

Ninguna vista ni template debe tomar decisiones de permisos sin pasar
por estas funciones. Así la lógica está centralizada y auditada.
"""

NIVEL_SUPERUSER = 100
NIVEL_STAFF = 90
NIVEL_ADMINISTRADOR = 80
NIVEL_COORDINADOR = 60
NIVEL_OPERADOR = 40
NIVEL_VOLUNTARIO = 20
NIVEL_USUARIO = 10


def nivel_de(user):
    """Devuelve el nivel jerárquico del usuario (0 si anónimo)."""
    if not user or not user.is_authenticated:
        return 0
    if user.is_superuser:
        return NIVEL_SUPERUSER
    if user.is_staff:
        return NIVEL_STAFF
    return {
        "ADMINISTRADOR": NIVEL_ADMINISTRADOR,
        "COORDINADOR": NIVEL_COORDINADOR,
        "OPERADOR": NIVEL_OPERADOR,
        "VOLUNTARIO": NIVEL_VOLUNTARIO,
        "USUARIO": NIVEL_USUARIO,
    }.get(getattr(user, "rol", "USUARIO"), NIVEL_USUARIO)


def puede_gestionar_usuarios(user):
    """True si el usuario puede al menos ver/crear la lista de usuarios."""
    return nivel_de(user) >= NIVEL_ADMINISTRADOR


def puede_crear_usuario(gestor, rol_nuevo):
    """
    ¿Puede `gestor` crear un usuario con rol `rol_nuevo`?
    - Solo puede crear roles de nivel ESTRICTAMENTE MENOR al suyo.
    - Un ADMINISTRADOR no puede crear otro ADMINISTRADOR desde el panel.
    """
    niveles_rol = {
        "ADMINISTRADOR": NIVEL_ADMINISTRADOR,
        "COORDINADOR": NIVEL_COORDINADOR,
        "OPERADOR": NIVEL_OPERADOR,
        "VOLUNTARIO": NIVEL_VOLUNTARIO,
        "USUARIO": NIVEL_USUARIO,
    }
    nivel_gestor = nivel_de(gestor)
    nivel_nuevo = niveles_rol.get(rol_nuevo, NIVEL_USUARIO)
    return nivel_gestor > nivel_nuevo


def puede_modificar_usuario(gestor, target):
    """
    ¿Puede `gestor` modificar (editar/desactivar) a `target`?
    """
    if not gestor.is_authenticated or not target:
        return False
    if gestor.pk == target.pk:
        return False  # nunca auto-gestión destructiva
    return nivel_de(gestor) > nivel_de(target)


def puede_eliminar_usuario(gestor, target):
    """Eliminar es más restrictivo: solo ADMINISTRADOR+ y no puede ser el último."""
    if not puede_modificar_usuario(gestor, target):
        return False
    # No se puede eliminar si es el último admin/staff/superuser
    from usuarios.models import Usuario
    if target.is_superuser or target.is_staff or target.rol == "ADMINISTRADOR":
        admins = Usuario.objects.filter(
            models_q_admins()
        ).exclude(pk=target.pk).count()
        return admins > 0
    return True


def models_q_admins():
    """Query reutilizable: todos los usuarios con nivel ADMIN o superior."""
    from django.db.models import Q
    return Q(is_staff=True) | Q(is_superuser=True) | Q(rol="ADMINISTRADOR")


def roles_que_puede_asignar(gestor):
    """
    Lista de roles que el gestor puede asignar al crear/editar usuarios.
    Solo roles de nivel estrictamente menor al suyo.
    """
    nivel = nivel_de(gestor)
    opciones = []
    if nivel > NIVEL_ADMINISTRADOR:
        opciones.append(("ADMINISTRADOR", "Administrador"))
    if nivel > NIVEL_COORDINADOR:
        opciones.append(("COORDINADOR", "Coordinador"))
    if nivel > NIVEL_OPERADOR:
        opciones.append(("OPERADOR", "Operador"))
    if nivel > NIVEL_VOLUNTARIO:
        opciones.append(("VOLUNTARIO", "Voluntario"))
    if nivel > NIVEL_USUARIO:
        opciones.append(("USUARIO", "Usuario"))
    return opciones
