from __future__ import annotations

import json

from operaciones.models import (
    CentroAyuda,
    Mision,
    Refugio,
    ReporteVial,
    Vehiculo,
    Via,
)


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


def vehiculos_geojson():
    queryset = (
        Vehiculo.objects
        .filter(activo=True, ubicacion__isnull=False)
        .select_related("centro", "conductor")
    )

    features = [
        _feature(
            vehiculo.ubicacion,
            {
                "id": str(vehiculo.id),
                "placa": vehiculo.placa,
                "tipo": vehiculo.get_tipo_display(),
                "tipo_codigo": vehiculo.tipo,
                "estado_operativo": vehiculo.estado_operativo,
                "estado_operativo_label": (
                    vehiculo.get_estado_operativo_display()
                ),
                "capacidad_kg": str(vehiculo.capacidad_kg),
                "centro": vehiculo.centro.nombre if vehiculo.centro else None,
                "conductor": (
                    vehiculo.conductor.get_full_name()
                    or vehiculo.conductor.username
                    if vehiculo.conductor
                    else None
                ),
                "observaciones": vehiculo.observaciones,
            },
        )
        for vehiculo in queryset
    ]

    return _feature_collection(features)


def misiones_geojson():
    queryset = (
        Mision.objects
        .filter(
            estado_mision__in=[
                Mision.Estados.PLANIFICADA,
                Mision.Estados.ASIGNADA,
                Mision.Estados.EN_RUTA,
            ]
        )
        .select_related("vehiculo", "coordinador")
    )

    features = []

    for mision in queryset:
        propiedades_base = {
            "id": str(mision.id),
            "codigo": mision.codigo,
            "nombre": mision.nombre,
            "descripcion": mision.descripcion,
            "estado_mision": mision.estado_mision,
            "estado_mision_label": mision.get_estado_mision_display(),
            "modo_ruta": mision.modo_ruta,
            "modo_ruta_label": mision.get_modo_ruta_display(),
            "prioridad": mision.prioridad,
            "vehiculo": (
                mision.vehiculo.placa
                if mision.vehiculo
                else None
            ),
            "coordinador": (
                mision.coordinador.get_full_name()
                or mision.coordinador.username
                if mision.coordinador
                else None
            ),
            "distancia_km": (
                str(mision.distancia_km)
                if mision.distancia_km is not None
                else None
            ),
            "tiempo_estimado_minutos": (
                mision.tiempo_estimado_minutos
            ),
        }

        # Ruta calculada.
        if mision.ruta:
            ruta_properties = {
                **propiedades_base,
                "geometria_tipo": "ruta",
            }

            features.append(
                _feature(
                    mision.ruta,
                    ruta_properties,
                )
            )

        # Origen y destino siempre disponibles.
        features.append(
            _feature(
                mision.origen,
                {
                    "id": str(mision.id),
                    "codigo": mision.codigo,
                    "nombre": mision.nombre,
                    "estado_mision": mision.estado_mision,
                    "estado_mision_label": (
                        mision.get_estado_mision_display()
                    ),
                    "prioridad": mision.prioridad,
                    "punto": "origen",
                },
            )
        )

        features.append(
            _feature(
                mision.destino,
                {
                    "id": str(mision.id),
                    "codigo": mision.codigo,
                    "nombre": mision.nombre,
                    "estado_mision": mision.estado_mision,
                    "estado_mision_label": (
                        mision.get_estado_mision_display()
                    ),
                    "prioridad": mision.prioridad,
                    "punto": "destino",
                },
            )
        )

    return _feature_collection(features)
