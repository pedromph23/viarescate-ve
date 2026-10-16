"""
Seed de datos mínimos para probar el pipeline de IA.

Uso:
    python manage.py seed_test_ia
    python manage.py seed_test_ia --limpiar   # borra todo primero
"""
from datetime import timedelta
from decimal import Decimal

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Estado, Municipio, Parroquia
from operaciones.models import (
    Mision,
    Necesidad,
    Recurso,
    Refugio,
)


class Command(BaseCommand):
    help = "Crea datos de prueba para el pipeline de IA."

    def add_arguments(self, parser):
        parser.add_argument("--limpiar", action="store_true")

    def handle(self, *args, **options):
        if options["limpiar"]:
            self.stdout.write(self.style.WARNING("Limpiando datos previos..."))
            Necesidad.objects.filter(
                recurso__nombre__startswith="[TEST-IA]"
            ).delete()
            Mision.objects.filter(codigo__startswith="TEST-IA").delete()
            Recurso.objects.filter(nombre__startswith="[TEST-IA]").delete()

        # --- Estado/Municipio/Parroquia (reusar si existen) ---
        # Buscamos por nombre (que es el unique) y solo creamos si no existe.
        estado = Estado.objects.filter(nombre="Distrito Capital").first()
        if not estado:
            estado = Estado.objects.filter(codigo="DC").first()
        if not estado:
            estado = Estado.objects.create(nombre="Distrito Capital", codigo="DC")
        self.stdout.write(f"  → Estado: {estado.nombre} (codigo={estado.codigo})")

        municipio = Municipio.objects.filter(
            estado=estado, nombre="Libertador"
        ).first()
        if not municipio:
            municipio = Municipio.objects.filter(
                estado=estado, codigo="LIB"
            ).first()
        if not municipio:
            municipio = Municipio.objects.create(
                estado=estado, nombre="Libertador", codigo="LIB"
            )
        self.stdout.write(f"  → Municipio: {municipio.nombre}")

        parroquia = Parroquia.objects.filter(
            municipio=municipio, nombre="Altagracia"
        ).first()
        if not parroquia:
            parroquia = Parroquia.objects.filter(
                municipio=municipio, codigo="ALT"
            ).first()
        if not parroquia:
            parroquia = Parroquia.objects.create(
                municipio=municipio, nombre="Altagracia", codigo="ALT"
            )
        self.stdout.write(f"  → Parroquia: {parroquia.nombre}")

        # --- 3 Recursos ---
        recursos = []
        for nombre, unidad in [
            ("[TEST-IA] Agua potable", "litros"),
            ("[TEST-IA] Alimentos no perecederos", "kg"),
            ("[TEST-IA] Medicamentos básicos", "unidades"),
        ]:
            r, _ = Recurso.objects.get_or_create(
                nombre=nombre,
                defaults={"unidad": unidad},
            )
            recursos.append(r)
        self.stdout.write(f"  → {len(recursos)} recursos")

        # --- 2 Refugios ---
        refugios = []
        for nombre, lat, lng in [
            ("[TEST-IA] Refugio Petare", 10.4777, -66.8097),
            ("[TEST-IA] Refugio Catia", 10.5100, -66.9500),
        ]:
            r, _ = Refugio.objects.get_or_create(
                nombre=nombre,
                defaults={
                    "estado": estado,
                    "municipio": municipio,
                    "parroquia": parroquia,
                    "ubicacion": Point(lng, lat, srid=4326),
                    "capacidad": 200,
                    "ocupacion": 80,
                    "direccion": "Dirección de prueba IA",
                },
            )
            refugios.append(r)
        self.stdout.write(f"  → {len(refugios)} refugios")

        # --- Necesidades (históricas y actuales) ---
        hoy = timezone.now()
        creadas = 0
        for refugio in refugios:
            for recurso in recursos:
                # Histórica hace 60 días
                Necesidad.objects.get_or_create(
                    refugio=refugio,
                    recurso=recurso,
                    defaults={
                        "cantidad_requerida": Decimal("500.00"),
                        "cantidad_recibida": Decimal("200.00"),
                        "prioridad": "ALTA",
                        "estado": "PARCIAL",
                        "fecha_requerida": hoy + timedelta(days=5),
                        "observaciones": "Seed IA",
                    },
                )
                creadas += 1
        self.stdout.write(f"  → {creadas} necesidades")

        # --- Misiones activas ---
        creadas_m = 0
        for i, refugio in enumerate(refugios):
            codigo = f"TEST-IA-{i+1:03d}"
            if Mision.objects.filter(codigo=codigo).exists():
                continue
            Mision.objects.create(
                codigo=codigo,
                nombre=f"Misión de prueba {i+1}",
                estado_mision="PLANIFICADA",
                modo_ruta="HUMANITARIA",
                origen=Point(-66.9036, 10.4806, srid=4326),  # Caracas
                destino=refugio.ubicacion,
                prioridad=4,
                fecha_salida_planificada=hoy - timedelta(hours=2),  # ya pasó → riesgo
                fecha_entrega_estimada=hoy + timedelta(hours=3),
                observaciones="Seed IA — misión con riesgo",
            )
            creadas_m += 1
        self.stdout.write(f"  → {creadas_m} misiones")

        self.stdout.write(self.style.SUCCESS("\n[OK] Seed completo."))
