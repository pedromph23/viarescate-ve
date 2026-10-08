from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import render

from .models import (
    CentroAyuda,
    Inventario,
    Mision,
    Refugio,
    ReporteVial,
    Vehiculo,
)


@login_required
def centro_operativo(request):
    contexto = {
        "centros_activos": CentroAyuda.objects.filter(
            activo=True
        ).count(),
        "refugios_activos": Refugio.objects.filter(
            activo=True
        ).count(),
        "vehiculos_disponibles": Vehiculo.objects.filter(
            activo=True,
            estado_operativo=Vehiculo.Estados.DISPONIBLE,
        ).count(),
        "vehiculos_en_ruta": Vehiculo.objects.filter(
            activo=True,
            estado_operativo=Vehiculo.Estados.EN_RUTA,
        ).count(),
        "misiones_planificadas": Mision.objects.filter(
            estado_mision=Mision.Estados.PLANIFICADA,
        ).count(),
        "misiones_en_ruta": Mision.objects.filter(
            estado_mision=Mision.Estados.EN_RUTA,
        ).count(),
        "incidencias_activas": ReporteVial.objects.filter(
            estado_reporte__in=[
                ReporteVial.Estados.PENDIENTE,
                ReporteVial.Estados.CONFIRMADO,
            ]
        ).count(),
        "inventario_bajo_minimo": Inventario.objects.filter(
            cantidad__lt=models.F("minimo"),
        ).count(),
    }

    return render(
        request,
        "operaciones/centro.html",
        contexto,
    )
