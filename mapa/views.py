from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from .services import (
    centros_ayuda_geojson,
    reportes_viales_geojson,
    refugios_geojson,
    vehiculos_geojson,
    misiones_geojson,
    vias_geojson,
)


def mapa_publico(request):
    return render(request, "mapa/mapa.html")


def centros_ayuda_geojson_view(request):
    return JsonResponse(centros_ayuda_geojson())


def refugios_geojson_view(request):
    return JsonResponse(refugios_geojson())


def vias_geojson_view(request):
    return JsonResponse(vias_geojson())


def reportes_viales_geojson_view(request):
    return JsonResponse(reportes_viales_geojson())


@login_required
def vehiculos_geojson_view(request):
    return JsonResponse(vehiculos_geojson())


@login_required
def misiones_geojson_view(request):
    return JsonResponse(misiones_geojson())
