from rest_framework.routers import DefaultRouter

from .views import (
    AuditLogViewSet,
    CentroAyudaViewSet,
    InventarioViewSet,
    MisionViewSet,
    MovimientoInventarioViewSet,
    RecursoViewSet,
    RefugioViewSet,
    ReporteVialViewSet,
    VehiculoViewSet,
    ViaViewSet,
)

from .views_prediccion import (
    AlertaPredictivaViewSet,
    PrediccionDemandaViewSet,
    PrediccionMisionViewSet,
)

router = DefaultRouter()

router.register(
    r"centros-ayuda",
    CentroAyudaViewSet,
    basename="centro-ayuda",
)

router.register(
    r"refugios",
    RefugioViewSet,
    basename="refugio",
)

router.register(
    r"vias",
    ViaViewSet,
    basename="via",
)

router.register(
    r"reportes-viales",
    ReporteVialViewSet,
    basename="reporte-vial",
)

router.register(
    r"vehiculos",
    VehiculoViewSet,
    basename="vehiculo",
)

router.register(
    r"misiones",
    MisionViewSet,
    basename="mision",
)

router.register(
    r"recursos",
    RecursoViewSet,
    basename="recurso",
)

router.register(
    r"inventario",
    InventarioViewSet,
    basename="inventario",
)

router.register(
    r"movimientos-inventario",
    MovimientoInventarioViewSet,
    basename="movimiento-inventario",
)

router.register(
    r"auditoria",
    AuditLogViewSet,
    basename="auditoria",
)

# Predicciones / IA
router.register(
    r"predicciones/demanda",
    PrediccionDemandaViewSet,
    basename="prediccion-demanda",
)
router.register(
    r"predicciones/misiones",
    PrediccionMisionViewSet,
    basename="prediccion-mision",
)
router.register(
    r"alertas-predictivas",
    AlertaPredictivaViewSet,
    basename="alerta-predictiva",
)

urlpatterns = router.urls
