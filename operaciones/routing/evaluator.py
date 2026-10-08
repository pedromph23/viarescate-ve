from __future__ import annotations

from dataclasses import dataclass

from django.contrib.gis.geos import LineString

from operaciones.models import ReporteVial, Via


@dataclass(frozen=True)
class RouteEvaluation:
    """Evaluación operacional de una ruta candidata."""

    blocked: bool
    risk_score: float
    distance_meters: float
    duration_seconds: float
    via_ids: tuple[str, ...] = ()
    report_ids: tuple[str, ...] = ()

    @property
    def humanitarian_score(self) -> float:
        """
        Costo combinado para planificación humanitaria.

        El riesgo domina sobre pequeñas diferencias de distancia y tiempo.
        """
        return (
            self.risk_score * 100.0
            + (self.distance_meters / 1000.0)
            + (self.duration_seconds / 60.0) * 0.05
        )


class RouteEvaluator:
    """Evalúa una ruta frente al estado vial y los reportes operativos."""

    VIA_RISK_WEIGHTS = {
        Via.Estados.NORMAL: 0.0,
        Via.Estados.PRECAUCION: 10.0,
        Via.Estados.AFECTADA: 35.0,
        Via.Estados.CRITICA: 70.0,
        Via.Estados.CERRADA: float("inf"),
    }

    REPORT_STATE_WEIGHTS = {
        ReporteVial.Estados.CONFIRMADO: 1.0,
        ReporteVial.Estados.PENDIENTE: 0.4,
        ReporteVial.Estados.RECHAZADO: 0.0,
        ReporteVial.Estados.RESUELTO: 0.0,
    }

    def evaluate(
        self,
        geometry: LineString,
        *,
        distance_meters: float,
        duration_seconds: float,
    ) -> RouteEvaluation:
        vias = list(
            Via.objects.filter(
                activa=True,
                geometria__intersects=geometry,
            ).only(
                "id",
                "estado_vial",
            )
        )

        blocked = any(
            via.estado_vial == Via.Estados.CERRADA
            for via in vias
        )

        risk_score = sum(
            self.VIA_RISK_WEIGHTS.get(
                via.estado_vial,
                0.0,
            )
            for via in vias
            if via.estado_vial != Via.Estados.CERRADA
        )

        reportes = list(
            ReporteVial.objects.filter(
                via_id__in=[via.id for via in vias],
            ).only(
                "id",
                "estado_reporte",
                "severidad",
            )
        )

        for reporte in reportes:
            state_weight = self.REPORT_STATE_WEIGHTS.get(
                reporte.estado_reporte,
                0.0,
            )

            risk_score += (
                float(reporte.severidad)
                * 10.0
                * state_weight
            )

        return RouteEvaluation(
            blocked=blocked,
            risk_score=risk_score,
            distance_meters=float(distance_meters),
            duration_seconds=float(duration_seconds),
            via_ids=tuple(str(via.id) for via in vias),
            report_ids=tuple(str(reporte.id) for reporte in reportes),
        )
