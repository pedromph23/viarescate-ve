from rest_framework.permissions import BasePermission


class Roles:
    ADMINISTRADOR = "ADMINISTRADOR"
    COORDINADOR = "COORDINADOR"
    OPERADOR = "OPERADOR"
    VOLUNTARIO = "VOLUNTARIO"
    USUARIO = "USUARIO"


class IsAuthenticatedRole(BasePermission):
    """
    Permiso base: exige autenticación y un rol válido.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return bool(getattr(user, "rol", None))


class IsAdministrador(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.rol == Roles.ADMINISTRADOR
        )


class IsCoordinadorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.rol
            in {
                Roles.ADMINISTRADOR,
                Roles.COORDINADOR,
            }
        )


class IsOperadorOrAbove(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.rol
            in {
                Roles.ADMINISTRADOR,
                Roles.COORDINADOR,
                Roles.OPERADOR,
            }
        )


class IsVoluntarioOrAbove(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.rol
            in {
                Roles.ADMINISTRADOR,
                Roles.COORDINADOR,
                Roles.OPERADOR,
                Roles.VOLUNTARIO,
            }
        )


class ReadOnlyOrAuthenticatedRole(BasePermission):
    """
    GET/HEAD/OPTIONS pueden ser públicos.
    Las operaciones de escritura requieren usuario autenticado con rol.
    """

    SAFE_METHODS = ("GET", "HEAD", "OPTIONS")

    def has_permission(self, request, view):
        if request.method in self.SAFE_METHODS:
            return True

        user = request.user

        return (
            user
            and user.is_authenticated
            and bool(getattr(user, "rol", None))
        )


class AuditLogPermission(BasePermission):
    """
    La auditoría nunca puede modificarse desde la API.
    Solo administradores y coordinadores pueden consultarla.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if request.method not in ("GET", "HEAD", "OPTIONS"):
            return False

        return user.rol in {
            Roles.ADMINISTRADOR,
            Roles.COORDINADOR,
        }
