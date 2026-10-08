class RoutingError(Exception):
    """Error base del motor de rutas."""


class RoutingConfigurationError(RoutingError):
    """La configuración del proveedor de rutas es inválida."""


class RoutingProviderError(RoutingError):
    """El proveedor externo no pudo calcular la ruta."""


class NoRouteFoundError(RoutingError):
    """No existe una ruta válida entre origen y destino."""


class RouteValidationError(RoutingError):
    """La ruta obtenida no cumple las reglas operativas."""
