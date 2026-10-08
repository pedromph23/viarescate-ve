from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from django.contrib.gis.geos import LineString, Point


@dataclass(frozen=True)
class RouteCandidate:
    """Ruta devuelta por un proveedor externo."""

    geometry: LineString
    distance_meters: float
    duration_seconds: float


@dataclass(frozen=True)
class RouteResult:
    """Resultado normalizado utilizado por VíaRescate VE."""

    geometry: LineString
    distance_km: float
    duration_minutes: int
    provider: str
    candidates_considered: int = 1


class RouteProvider(Protocol):
    """Contrato común para cualquier proveedor de rutas."""

    name: str

    def calculate_routes(
        self,
        origin: Point,
        destination: Point,
        *,
        alternatives: bool = True,
    ) -> list[RouteCandidate]:
        """Calcula una o más rutas entre dos puntos."""
        ...
