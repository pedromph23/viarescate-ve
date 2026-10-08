from __future__ import annotations

import json

from operaciones.models import CentroAyuda, Refugio, ReporteVial, Via


def _feature(geometry, properties):
    return {
        "type": "Feature",
        "geometry": json.loads(geometry.geojson),
        "properties": properties,
    }


def _feature_collection(features):
    return {
        "type": "FeatureCollection",
        "features": features,
    }


def centros_ayuda_geojson():
    queryset = (
        CentroAyuda.objects
        .filter(activo=True)
        .select_related("estado", "municipio", "parroquia")
    )

    features = [
        _feature(
            centro.ubicacion,
            {
                "id": str(centro.id),
                "nombre": centro.nombre,
                "tipo": centro.get_tipo_display(),
                "estado": centro.estado.nombre,
                "municipio": centro.municipio.nombre,
                "parroquia": centro.parroquia.nombre,
                "direccion": centro.direccion,
                "telefono": centro.telefono,
                "capacidad": centro.capacidad,
            },
        )
        for centro in queryset
    ]

    return _feature_collection(features)


def refugios_geojson():
    queryset = (
        Refugio.objects
        .filter(activo=True)
        .select_related("estado", "municipio", "parroquia")
    )

    features = [
        _feature(
            refugio.ubicacion,
            {
                "id": str(refugio.id),
                "nombre": refugio.nombre,
                "estado_operativo": refugio.estado_operativo,
                "estado_operativo_label": refugio.get_estado_operativo_display(),
                "estado": refugio.estado.nombre,
                "municipio": refugio.municipio.nombre,
                "parroquia": refugio.parroquia.nombre,
                "direccion": refugio.direccion,
                "telefono": refugio.telefono,
                "capacidad": refugio.capacidad,
                "ocupacion": refugio.ocupacion,
                "porcentaje_ocupacion": (
                    round((refugio.ocupacion / refugio.capacidad) * 100, 1)
                    if refugio.capacidad
                    else 0
                ),
            },
        )
        for refugio in queryset
    ]

    return _feature_collection(features)


def vias_geojson():
    queryset = (
        Via.objects
        .filter(activa=True)
        .select_related("estado")
    )

    features = [
        _feature(
            via.geometria,
            {
                "id": str(via.id),
                "nombre": via.nombre,
                "codigo": via.codigo,
                "estado_vial": via.estado_vial,
                "estado_vial_label": via.get_estado_vial_display(),
                "estado": via.estado.nombre,
                "velocidad_referencial": via.velocidad_referencial,
            },
        )
        for via in queryset
    ]

    return _feature_collection(features)


def reportes_viales_geojson():
    queryset = (
        ReporteVial.objects
        .filter(
            estado_reporte__in=[
                ReporteVial.Estados.PENDIENTE,
                ReporteVial.Estados.CONFIRMADO,
            ]
        )
        .select_related("via")
    )

    features = [
        _feature(
            reporte.ubicacion,
            {
                "id": str(reporte.id),
                "tipo": reporte.tipo,
                "tipo_label": reporte.get_tipo_display(),
                "estado_reporte": reporte.estado_reporte,
                "estado_reporte_label": reporte.get_estado_reporte_display(),
                "titulo": reporte.titulo,
                "descripcion": reporte.descripcion,
                "severidad": reporte.severidad,
                "via": reporte.via.nombre if reporte.via else None,
                "reportado_en": reporte.reportado_en.isoformat(),
            },
        )
        for reporte in queryset
    ]

    return _feature_collection(features)
