from django.shortcuts import render

from operaciones.models import CentroAyuda, Refugio, ReporteVial, Via


def inicio_publico(request):
    contexto = {
        "centros_activos": CentroAyuda.objects.filter(activo=True).count(),
        "refugios_activos": Refugio.objects.filter(activo=True).count(),
        "vias_activas": Via.objects.filter(activa=True).count(),
        "incidencias_activas": ReporteVial.objects.filter(
            estado_reporte__in=[
                ReporteVial.Estados.PENDIENTE,
                ReporteVial.Estados.CONFIRMADO,
            ]
        ).count(),
    }

    return render(request, "public/home.html", contexto)
