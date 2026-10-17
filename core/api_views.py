"""
Endpoints JSON para cascading selects (estado → municipio → parroquia).
Son datos públicos de división territorial; protegidos por login por consistencia.
"""
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Municipio, Parroquia


@login_required
def municipios_por_estado(request, estado_id):
    """Lista de municipios de un estado, ordenados por nombre."""
    municipios = (
        Municipio.objects.filter(estado_id=estado_id)
        .order_by("nombre")
        .values("id", "nombre")
    )
    return JsonResponse({"municipios": list(municipios)})


@login_required
def parroquias_por_municipio(request, municipio_id):
    """Lista de parroquias de un municipio, ordenadas por nombre."""
    parroquias = (
        Parroquia.objects.filter(municipio_id=municipio_id)
        .order_by("nombre")
        .values("id", "nombre")
    )
    return JsonResponse({"parroquias": list(parroquias)})
