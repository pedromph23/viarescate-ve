from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.contrib.gis.geos import LineString, Point

from .base import RouteCandidate
from .exceptions import (
    RoutingConfigurationError,
    RoutingProviderError,
)


class OSRMProvider:
    """Proveedor de rutas basado en OSRM."""

    name = "osrm"

    def __init__(
        self,
        base_url: str | None = None,
        *,
        timeout: int | None = None,
    ):
        self.base_url = (
            base_url
            or getattr(
                settings,
                "ROUTING_OSRM_BASE_URL",
                "https://router.project-osrm.org",
            )
        ).rstrip("/")

        self.timeout = timeout or getattr(
            settings,
            "ROUTING_TIMEOUT_SECONDS",
            10,
        )

        if not self.base_url:
            raise RoutingConfigurationError(
                "ROUTING_OSRM_BASE_URL no puede estar vacío."
            )

    @staticmethod
    def _coordinates(point: Point) -> str:
        return f"{point.x},{point.y}"

    def calculate_routes(
        self,
        origin: Point,
        destination: Point,
        *,
        alternatives: bool = True,
    ) -> list[RouteCandidate]:
        if origin is None or destination is None:
            raise RoutingProviderError(
                "El origen y el destino son obligatorios."
            )

        if origin.srid != 4326:
            origin = origin.transform(4326, clone=True)

        if destination.srid != 4326:
            destination = destination.transform(4326, clone=True)

        coordinates = (
            f"{self._coordinates(origin)};"
            f"{self._coordinates(destination)}"
        )

        query = urlencode(
            {
                "overview": "full",
                "geometries": "geojson",
                "steps": "false",
                "alternatives": "true" if alternatives else "false",
            }
        )

        url = f"{self.base_url}/route/v1/driving/{coordinates}?{query}"

        request = Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "ViaRescateVE/1.0",
            },
            method="GET",
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = json.load(response)
        except HTTPError as exc:
            raise RoutingProviderError(
                f"OSRM respondió con HTTP {exc.code}."
            ) from exc
        except URLError as exc:
            raise RoutingProviderError(
                "No fue posible comunicarse con el proveedor OSRM."
            ) from exc
        except TimeoutError as exc:
            raise RoutingProviderError(
                "La consulta al proveedor OSRM agotó el tiempo de espera."
            ) from exc
        except (OSError, ValueError) as exc:
            raise RoutingProviderError(
                "La respuesta del proveedor OSRM no pudo procesarse."
            ) from exc

        if payload.get("code") != "Ok":
            message = payload.get("message") or "OSRM no pudo calcular la ruta."
            raise RoutingProviderError(message)

        candidates = []

        for route in payload.get("routes", []):
            geometry = route.get("geometry", {})
            coordinates = geometry.get("coordinates", [])

            if len(coordinates) < 2:
                continue

            try:
                line = LineString(
                    [(float(lon), float(lat)) for lon, lat in coordinates],
                    srid=4326,
                )
            except (TypeError, ValueError):
                continue

            candidates.append(
                RouteCandidate(
                    geometry=line,
                    distance_meters=float(route.get("distance", 0)),
                    duration_seconds=float(route.get("duration", 0)),
                )
            )

        if not candidates:
            raise RoutingProviderError(
                "OSRM no devolvió ninguna geometría de ruta válida."
            )

        return candidates
