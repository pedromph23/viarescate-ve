"""Vistas públicas de reportes (sin login requerido)."""
from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.utils import timezone

from core.models import Estado
from .forms_publico import ReportePublicoForm


# Límites anti-spam
MIN_SEGUNDOS_ENTRE_REPORTES = 180      # 3 minutos
MAX_REPORTES_POR_DIA = 5


def _get_client_ip(request):
    """IP real del cliente respetando proxies (Vercel)."""
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "0.0.0.0")


def _contexto_form(form):
    return {
        "form": form,
        "estados_centroides": {
            str(e.id): {"lat": e.centroide_lat, "lng": e.centroide_lng}
            for e in Estado.objects.exclude(centroide_lat__isnull=True)
                                    .exclude(centroide_lng__isnull=True)
        },
    }


def reportar_publico(request):
    """Formulario público de reporte vial con rate limiting."""
    ip = _get_client_ip(request)
    cache_key_last = f"reporte_pub:last:{ip}"
    cache_key_count = f"reporte_pub:count:{ip}"

    # Rate limit: ventana entre reportes
    ultimo = cache.get(cache_key_last)
    if ultimo:
        diff = timezone.now().timestamp() - ultimo
        if diff < MIN_SEGUNDOS_ENTRE_REPORTES:
            espera = int(MIN_SEGUNDOS_ENTRE_REPORTES - diff)
            messages.error(
                request,
                f"Debes esperar {espera} segundos antes de enviar otro reporte."
            )
            return render(request, "reportes/publico.html", _contexto_form(ReportePublicoForm()))

    # Rate limit: máximo diario
    count_hoy = cache.get(cache_key_count, 0)
    if count_hoy >= MAX_REPORTES_POR_DIA:
        messages.error(
            request,
            "Has alcanzado el límite de reportes diarios desde tu conexión. "
            "Intenta mañana o contacta al equipo si es urgente."
        )
        return render(request, "reportes/publico.html", _contexto_form(ReportePublicoForm()))

    if request.method == "POST":
        form = ReportePublicoForm(request.POST, request.FILES)
        if form.is_valid():
            reporte = form.save()
            cache.set(cache_key_last, timezone.now().timestamp(),
                      timeout=MIN_SEGUNDOS_ENTRE_REPORTES * 2)
            cache.set(cache_key_count, count_hoy + 1, timeout=86400)
            return redirect("operaciones:reporte_publico_gracias", pk=reporte.id)
    else:
        form = ReportePublicoForm()

    return render(request, "reportes/publico.html", _contexto_form(form))


def reporte_publico_gracias(request, pk):
    """Confirmación después de enviar un reporte."""
    return render(request, "reportes/gracias.html", {"reporte_id": pk})
