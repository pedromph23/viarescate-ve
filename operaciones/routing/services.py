from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError

from operaciones.models import Mision

from .base import RouteProvider, RouteResult
from .exceptions import NoRouteFoundError, RoutingError, RouteValidationError
from .evaluator import RouteEvaluation, RouteEvaluator
from .providers import OSRMProvider


class RouteService:
    """Motor central de planificación de rutas de VíaRescate VE."""

    def __init__(
        self,
        provider: RouteProvider | None = None,
        evaluator: RouteEvaluator | None = None,
    ):
        self.provider = provider or OSRMProvider()
        self.evaluator = evaluator or RouteEvaluator()

    def calculate_for_mission(
        self,
        mission: Mision,
        *,
        save: bool = False,
    ) -> RouteResult:
        if not mission.origen or not mission.destino:
            raise ValidationError(
                "La misión debe tener origen y destino."
            )

        if mission.origen.equals(mission.destino):
            raise ValidationError(
                "El origen y el destino de la misión no pueden coincidir."
            )

        try:
            candidates = self.provider.calculate_routes(
                mission.origen,
                mission.destino,
                alternatives=True,
            )
        except RoutingError:
            raise

        if not candidates:
            raise NoRouteFoundError(
                "No se encontró una ruta válida para la misión."
            )

        evaluated = [
            (
                candidate,
                self.evaluator.evaluate(
                    candidate.geometry,
                    distance_meters=candidate.distance_meters,
                    duration_seconds=candidate.duration_seconds,
                ),
            )
            for candidate in candidates
        ]

        valid_candidates = [
            item
            for item in evaluated
            if not item[1].blocked
        ]

        if not valid_candidates:
            raise RouteValidationError(
                "Todas las rutas candidatas atraviesan vías cerradas."
            )

        candidate, evaluation = self._select_candidate(
            valid_candidates,
            mission.modo_ruta,
        )

        distance_km = (
            Decimal(str(candidate.distance_meters / 1000))
            .quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            )
        )

        duration_minutes = max(
            1,
            round(candidate.duration_seconds / 60),
        )

        result = RouteResult(
            geometry=candidate.geometry,
            distance_km=float(distance_km),
            duration_minutes=duration_minutes,
            provider=self.provider.name,
            candidates_considered=len(candidates),
        )

        if save:
            mission.ruta = result.geometry
            mission.distancia_km = distance_km
            mission.tiempo_estimado_minutos = result.duration_minutes
            mission.save(
                update_fields=(
                    "ruta",
                    "distancia_km",
                    "tiempo_estimado_minutos",
                )
            )

        return result

    @staticmethod
    def _select_candidate(
        candidates: list[tuple[object, RouteEvaluation]],
        mode: str,
    ):
        if not candidates:
            raise NoRouteFoundError(
                "No existen rutas operativamente válidas."
            )

        if mode == Mision.ModosRuta.MAS_CORTA:
            return min(
                candidates,
                key=lambda item: item[0].distance_meters,
            )

        if mode == Mision.ModosRuta.MAS_RAPIDA:
            return min(
                candidates,
                key=lambda item: item[0].duration_seconds,
            )

        if mode == Mision.ModosRuta.MAS_SEGURA:
            return min(
                candidates,
                key=lambda item: (
                    item[1].risk_score,
                    item[0].distance_meters,
                    item[0].duration_seconds,
                ),
            )

        return min(
            candidates,
            key=lambda item: item[1].humanitarian_score,
        )
