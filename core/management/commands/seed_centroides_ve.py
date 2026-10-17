"""
Carga los centroides (capitales) de los 24 estados de Venezuela.
Busca por nombre (más robusto que código, que puede variar).

Uso:
    python manage.py seed_centroides_ve
    python manage.py seed_centroides_ve --overwrite  # sobrescribe aunque ya tenga valor
"""
from django.core.management.base import BaseCommand

from core.models import Estado


# (nombre, lat, lng, capital)
CENTROIDES = [
    ("Distrito Capital", 10.4806, -66.9036, "Caracas"),
    ("Anzoátegui",       10.1333, -64.6833, "Barcelona"),
    ("Aragua",           10.2500, -67.6000, "Maracay"),
    ("Carabobo",         10.1667, -68.0000, "Valencia"),
    ("Barinas",          8.6333,  -70.2000, "Barinas"),
    ("Bolívar",          8.1167,  -63.5500, "Ciudad Bolívar"),
    ("Cojedes",          9.6667,  -68.5833, "San Carlos"),
    ("Falcón",           11.4167, -69.6667, "Coro"),
    ("Guárico",          9.9167,  -67.3667, "San Juan de los Morros"),
    ("Lara",             10.0667, -69.3167, "Barquisimeto"),
    ("Mérida",           8.5833,  -71.1333, "Mérida"),
    ("Miranda",          10.3500, -67.0333, "Los Teques"),
    ("Monagas",          9.7500,  -63.1833, "Maturín"),
    ("Nueva Esparta",    11.0333, -63.8667, "La Asunción"),
    ("Portuguesa",       9.0500,  -69.7500, "Guanare"),
    ("Sucre",            10.4667, -64.1667, "Cumaná"),
    ("Táchira",          7.7667,  -72.2333, "San Cristóbal"),
    ("Trujillo",         9.3667,  -70.4333, "Trujillo"),
    ("Yaracuy",          10.3333, -68.7500, "San Felipe"),
    ("Zulia",            10.6500, -71.6167, "Maracaibo"),
    ("Amazonas",         5.6631,  -67.6236, "Puerto Ayacucho"),
    ("Apure",            7.8833,  -67.4667, "San Fernando de Apure"),
    ("Delta Amacuro",    9.0667,  -62.0500, "Tucupita"),
    ("Vargas",           10.6000, -66.9333, "La Guaira"),
    ("La Guaira",        10.6000, -66.9333, "La Guaira"),  # alias
]


class Command(BaseCommand):
    help = "Carga los centroides de los estados de Venezuela."

    def add_arguments(self, parser):
        parser.add_argument("--overwrite", action="store_true",
                          help="Sobrescribe centroides existentes")

    def handle(self, *args, **options):
        overwrite = options["overwrite"]
        actualizados = 0
        no_encontrados = 0

        for nombre, lat, lng, capital in CENTROIDES:
            estados = Estado.objects.filter(nombre__iexact=nombre)

            if not estados.exists():
                no_encontrados += 1
                self.stdout.write(
                    self.style.WARNING(f"  ⚠ '{nombre}' no existe en la DB")
                )
                continue

            for estado in estados:
                cambios = []
                if overwrite or estado.centroide_lat is None:
                    estado.centroide_lat = lat
                    cambios.append("lat")
                if overwrite or estado.centroide_lng is None:
                    estado.centroide_lng = lng
                    cambios.append("lng")

                if cambios:
                    estado.save(update_fields=["centroide_lat", "centroide_lng"])
                    actualizados += 1
                    self.stdout.write(
                        f"  → {estado.nombre}: {lat}, {lng} ({capital})"
                    )

        self.stdout.write(self.style.SUCCESS(
            f"\n[OK] {actualizados} estados actualizados, "
            f"{no_encontrados} no encontrados."
        ))
