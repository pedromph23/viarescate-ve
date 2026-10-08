from django.contrib.gis.geos import LineString, Point
from django.core.management.base import BaseCommand, CommandError

from core.models import Estado, Municipio, Parroquia
from operaciones.models import CentroAyuda, Refugio, ReporteVial, Via


class Command(BaseCommand):
    help = (
        "Crea datos operacionales ficticios para desarrollo y pruebas. "
        "No modifica los datos territoriales maestros."
    )

    DEMO_PREFIX = "[DEMO]"

    def handle(self, *args, **options):
        estado = self._get_estado()
        municipio = self._get_municipio(estado)
        parroquia = self._get_parroquia(municipio)

        self.stdout.write(
            self.style.NOTICE(
                f"Territorio demo: {estado.nombre} → "
                f"{municipio.nombre} → {parroquia.nombre}"
            )
        )

        centro_1, _ = CentroAyuda.objects.update_or_create(
            nombre=f"{self.DEMO_PREFIX} Centro Logístico Caracas",
            defaults={
                "tipo": CentroAyuda.Tipos.LOGISTICO,
                "estado": estado,
                "municipio": municipio,
                "parroquia": parroquia,
                "ubicacion": Point(-66.9036, 10.4806, srid=4326),
                "direccion": "Ubicación ficticia para pruebas",
                "telefono": "+58 000-0000000",
                "capacidad": 500,
                "activo": True,
                "observaciones": (
                    "Registro ficticio de desarrollo. "
                    "No representa una instalación humanitaria real."
                ),
            },
        )

        centro_2, _ = CentroAyuda.objects.update_or_create(
            nombre=f"{self.DEMO_PREFIX} Centro de Distribución Oeste",
            defaults={
                "tipo": CentroAyuda.Tipos.DISTRIBUCION,
                "estado": estado,
                "municipio": municipio,
                "parroquia": parroquia,
                "ubicacion": Point(-66.9480, 10.4700, srid=4326),
                "direccion": "Ubicación ficticia para pruebas",
                "telefono": "+58 000-0000001",
                "capacidad": 300,
                "activo": True,
                "observaciones": (
                    "Registro ficticio de desarrollo. "
                    "No representa una instalación humanitaria real."
                ),
            },
        )

        Refugio.objects.update_or_create(
            nombre=f"{self.DEMO_PREFIX} Refugio Comunitario Norte",
            defaults={
                "estado": estado,
                "municipio": municipio,
                "parroquia": parroquia,
                "ubicacion": Point(-66.8900, 10.5100, srid=4326),
                "direccion": "Ubicación ficticia para pruebas",
                "telefono": "+58 000-0000010",
                "capacidad": 250,
                "ocupacion": 138,
                "estado_operativo": Refugio.Estados.DISPONIBLE,
                "activo": True,
                "observaciones": (
                    "Registro ficticio de desarrollo. "
                    "No representa un refugio real."
                ),
            },
        )

        Refugio.objects.update_or_create(
            nombre=f"{self.DEMO_PREFIX} Refugio de Emergencia Central",
            defaults={
                "estado": estado,
                "municipio": municipio,
                "parroquia": parroquia,
                "ubicacion": Point(-66.9150, 10.4550, srid=4326),
                "direccion": "Ubicación ficticia para pruebas",
                "telefono": "+58 000-0000011",
                "capacidad": 180,
                "ocupacion": 165,
                "estado_operativo": Refugio.Estados.DISPONIBLE,
                "activo": True,
                "observaciones": (
                    "Registro ficticio de desarrollo. "
                    "No representa un refugio real."
                ),
            },
        )

        via_1, _ = Via.objects.update_or_create(
            nombre=f"{self.DEMO_PREFIX} Corredor Humanitario Norte",
            defaults={
                "codigo": "DEMO-VIA-001",
                "estado": estado,
                "geometria": LineString(
                    [
                        (-66.9500, 10.4500),
                        (-66.9300, 10.4700),
                        (-66.9100, 10.4900),
                        (-66.8900, 10.5100),
                    ],
                    srid=4326,
                ),
                "estado_vial": Via.Estados.NORMAL,
                "velocidad_referencial": 50,
                "activa": True,
                "observaciones": "Geometría ficticia para pruebas GIS.",
            },
        )

        via_2, _ = Via.objects.update_or_create(
            nombre=f"{self.DEMO_PREFIX} Corredor Logístico Oeste",
            defaults={
                "codigo": "DEMO-VIA-002",
                "estado": estado,
                "geometria": LineString(
                    [
                        (-66.9700, 10.4600),
                        (-66.9500, 10.4700),
                        (-66.9300, 10.4750),
                        (-66.9100, 10.4800),
                    ],
                    srid=4326,
                ),
                "estado_vial": Via.Estados.PRECAUCION,
                "velocidad_referencial": 35,
                "activa": True,
                "observaciones": "Geometría ficticia para pruebas GIS.",
            },
        )

        ReporteVial.objects.update_or_create(
            titulo=f"{self.DEMO_PREFIX} Precaución en corredor logístico",
            defaults={
                "tipo": ReporteVial.Tipos.TRAFICO,
                "estado_reporte": ReporteVial.Estados.CONFIRMADO,
                "via": via_2,
                "ubicacion": Point(-66.9420, 10.4680, srid=4326),
                "descripcion": (
                    "Incidencia ficticia utilizada para probar "
                    "marcadores y estados del mapa."
                ),
                "severidad": 3,
                "reportado_por": None,
            },
        )

        ReporteVial.objects.update_or_create(
            titulo=f"{self.DEMO_PREFIX} Obstáculo temporal",
            defaults={
                "tipo": ReporteVial.Tipos.OBSTACULO,
                "estado_reporte": ReporteVial.Estados.PENDIENTE,
                "via": via_1,
                "ubicacion": Point(-66.9150, 10.4850, srid=4326),
                "descripcion": (
                    "Incidencia ficticia utilizada para probar "
                    "reportes pendientes en el mapa."
                ),
                "severidad": 2,
                "reportado_por": None,
            },
        )

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Datos demo creados/actualizados."))
        self.stdout.write(
            self.style.SUCCESS(
                "Centros: 2 | Refugios: 2 | Vías: 2 | Reportes viales: 2"
            )
        )
        self.stdout.write(
            self.style.WARNING(
                "Todos los registros anteriores son ficticios y solo deben "
                "utilizarse para desarrollo/pruebas."
            )
        )

    @staticmethod
    def _get_estado():
        estado = Estado.objects.filter(nombre__iexact="Distrito Capital").first()

        if estado is None:
            estado = Estado.objects.order_by("nombre").first()

        if estado is None:
            raise CommandError(
                "No existen Estados territoriales. "
                "Carga primero los datos maestros de Venezuela."
            )

        return estado

    @staticmethod
    def _get_municipio(estado):
        municipio = (
            Municipio.objects.filter(
                estado=estado,
                nombre__iexact="Libertador",
            ).first()
        )

        if municipio is None:
            municipio = Municipio.objects.filter(estado=estado).order_by(
                "nombre"
            ).first()

        if municipio is None:
            raise CommandError(
                f"El Estado '{estado.nombre}' no tiene Municipios."
            )

        return municipio

    @staticmethod
    def _get_parroquia(municipio):
        parroquia = Parroquia.objects.filter(
            municipio=municipio,
            nombre__iexact="Sucre",
        ).first()

        if parroquia is None:
            parroquia = Parroquia.objects.filter(
                municipio=municipio
            ).order_by("nombre").first()

        if parroquia is None:
            raise CommandError(
                f"El Municipio '{municipio.nombre}' no tiene Parroquias."
            )

        return parroquia
