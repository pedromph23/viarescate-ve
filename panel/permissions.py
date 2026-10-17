"""
Sistema centralizado de permisos por rol — VíaRescate VE.

Cada permiso es una acción granular (ver_X, crear_X, editar_X, eliminar_X).
Los decoradores y template tags consultan esta matriz.
"""

# Acciones base por modelo
VER = "ver"
CREAR = "crear"
EDITAR = "editar"
ELIMINAR = "eliminar"


def _permisos_modelo(modelo, *acciones):
    """Genera permisos tipo {accion}_{modelo}."""
    return {f"{a}_{modelo}" for a in acciones}


# ---------------------------------------------------------------------------
# MATRIZ DE PERMISOS POR ROL
# ---------------------------------------------------------------------------
MATRIZ = {
    "ADMINISTRADOR": (
        {"ver_dashboard"}
        | _permisos_modelo("centros", VER, CREAR, EDITAR, ELIMINAR)
        | _permisos_modelo("refugios", VER, CREAR, EDITAR, ELIMINAR)
        | _permisos_modelo("vias", VER, CREAR, EDITAR, ELIMINAR)
        | _permisos_modelo("reportes", VER, CREAR, EDITAR, ELIMINAR)
        | {"verificar_reportes"}
        | _permisos_modelo("necesidades", VER, CREAR, EDITAR, ELIMINAR)
        | _permisos_modelo("inventarios", VER, CREAR, EDITAR, ELIMINAR)
        | _permisos_modelo("movimientos", VER, CREAR)
        | _permisos_modelo("misiones", VER, CREAR, EDITAR, ELIMINAR)
        | _permisos_modelo("vehiculos", VER, CREAR, EDITAR, ELIMINAR)
        | _permisos_modelo("recursos", VER, CREAR, EDITAR, ELIMINAR)
        | _permisos_modelo("usuarios", VER, CREAR, EDITAR, ELIMINAR)
        | {"cambiar_roles"}
        | {"ver_auditoria"}
        | {"ver_predicciones"}
        | {"ver_alertas", "reconocer_alertas"}
    ),
    "COORDINADOR": (
        {"ver_dashboard"}
        | _permisos_modelo("centros", VER, CREAR, EDITAR, ELIMINAR)
        | _permisos_modelo("refugios", VER, CREAR, EDITAR, ELIMINAR)
        | _permisos_modelo("vias", VER, CREAR, EDITAR, ELIMINAR)
        | _permisos_modelo("reportes", VER, CREAR, EDITAR, ELIMINAR)
        | {"verificar_reportes"}
        | _permisos_modelo("necesidades", VER, CREAR, EDITAR, ELIMINAR)
        | _permisos_modelo("inventarios", VER, CREAR, EDITAR, ELIMINAR)
        | _permisos_modelo("movimientos", VER, CREAR)
        | _permisos_modelo("misiones", VER, CREAR, EDITAR, ELIMINAR)
        | _permisos_modelo("vehiculos", VER, CREAR, EDITAR, ELIMINAR)
        | _permisos_modelo("recursos", VER, CREAR, EDITAR, ELIMINAR)
        | _permisos_modelo("usuarios", VER)
        | {"ver_auditoria"}
        | {"ver_predicciones"}
        | {"ver_alertas", "reconocer_alertas"}
    ),
    "OPERADOR": (
        {"ver_dashboard"}
        | _permisos_modelo("centros", VER)
        | _permisos_modelo("refugios", VER)
        | _permisos_modelo("vias", VER)
        | _permisos_modelo("reportes", VER, CREAR)
        | _permisos_modelo("necesidades", VER, EDITAR)
        | _permisos_modelo("inventarios", VER, EDITAR)
        | _permisos_modelo("movimientos", VER, CREAR)
        | _permisos_modelo("misiones", VER, CREAR, EDITAR)
        | _permisos_modelo("vehiculos", VER)
        | _permisos_modelo("recursos", VER)
        | {"ver_predicciones"}
        | {"ver_alertas"}
    ),
    "VOLUNTARIO": (
        {"ver_dashboard"}
        | _permisos_modelo("centros", VER)
        | _permisos_modelo("refugios", VER)
        | _permisos_modelo("vias", VER)
        | _permisos_modelo("reportes", VER, CREAR)
        | _permisos_modelo("necesidades", VER)
        | _permisos_modelo("inventarios", VER)
        | _permisos_modelo("misiones", VER)
        | _permisos_modelo("vehiculos", VER)
    ),
    "USUARIO": set(),  # sin acceso al panel
}

# Los is_staff/is_superuser de Django tienen acceso total
PERMISOS_STAFF = MATRIZ["ADMINISTRADOR"]


def permisos_de(user):
    """Devuelve el set de permisos del usuario."""
    if not user.is_authenticated:
        return set()
    if user.is_superuser or user.is_staff:
        return PERMISOS_STAFF
    return MATRIZ.get(getattr(user, "rol", ""), set())


def tiene_permiso(user, permiso):
    """Chequea si un usuario tiene un permiso específico."""
    return permiso in permisos_de(user)


def puede_acceder_panel(user):
    """True si el usuario tiene al menos un permiso (para mostrar el enlace del navbar)."""
    return bool(permisos_de(user))
