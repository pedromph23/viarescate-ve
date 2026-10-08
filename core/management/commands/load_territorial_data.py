import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import Estado, Municipio, Parroquia


class Command(BaseCommand):
    help = (
        "Carga los datos territoriales maestros de Venezuela "
        "(Estados, Municipios y Parroquias) desde data/territorial."
    )

    DATA_DIR = Path("data/territorial")

    FILES = {
        "estados": "all-state.json",
        "municipios": "all-municipality.json",
        "parroquias": "all-parish.json",
    }

    EXPECTED_COUNTS = {
        "estados": 24,
        "municipios": 335,
        "parroquias": 1134,
    }

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Valida los datos sin modificar la base de datos.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        estados_data = self._load_json("estados")
        municipios_data = self._load_json("municipios")
        parroquias_data = self._load_json("parroquias")

        self._validate_counts(estados_data, "estados")
        self._validate_counts(municipios_data, "municipios")
        self._validate_counts(parroquias_data, "parroquias")

        self._validate_levels(
            estados_data,
            1,
            "Estados",
        )
        self._validate_levels(
            municipios_data,
            2,
            "Municipios",
        )
        self._validate_levels(
            parroquias_data,
            3,
            "Parroquias",
        )

        self._validate_relationships(
            estados_data,
            municipios_data,
            parroquias_data,
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Validación territorial completada correctamente."
            )
        )
        self.stdout.write(f"  Estados: {len(estados_data)}")
        self.stdout.write(f"  Municipios: {len(municipios_data)}")
        self.stdout.write(f"  Parroquias: {len(parroquias_data)}")

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "Modo --dry-run: no se modificó la base de datos."
                )
            )
            return

        with transaction.atomic():
            estados = self._upsert_estados(estados_data)
            municipios = self._upsert_municipios(
                municipios_data,
                estados,
            )
            parroquias = self._upsert_parroquias(
                parroquias_data,
                municipios,
            )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Datos territoriales cargados correctamente."
            )
        )
        self.stdout.write(
            f"  Estados procesados: {estados}"
        )
        self.stdout.write(
            f"  Municipios procesados: {municipios}"
        )
        self.stdout.write(
            f"  Parroquias procesadas: {parroquias}"
        )

        self._show_database_counts()

    def _load_json(self, key):
        path = self.DATA_DIR / self.FILES[key]

        if not path.exists():
            raise CommandError(
                f"No existe el archivo territorial requerido: {path}"
            )

        try:
            data = json.loads(
                path.read_text(encoding="utf-8")
            )
        except json.JSONDecodeError as exc:
            raise CommandError(
                f"JSON inválido en {path}: {exc}"
            ) from exc

        if not isinstance(data, list):
            raise CommandError(
                f"El archivo {path} debe contener una lista JSON."
            )

        return data

    def _validate_counts(self, data, key):
        expected = self.EXPECTED_COUNTS[key]
        actual = len(data)

        if actual != expected:
            raise CommandError(
                f"Cantidad inesperada para {key}: "
                f"se esperaban {expected}, se encontraron {actual}."
            )

    def _validate_levels(self, data, expected_level, label):
        invalid = [
            item.get("id")
            for item in data
            if item.get("level") != expected_level
        ]

        if invalid:
            raise CommandError(
                f"{label} con nivel incorrecto: {invalid[:10]}"
            )

    def _validate_relationships(
        self,
        estados_data,
        municipios_data,
        parroquias_data,
    ):
        estado_ids = {
            item["id"]
            for item in estados_data
        }

        municipio_ids = {
            item["id"]
            for item in municipios_data
        }

        parroquia_ids = {
            item["id"]
            for item in parroquias_data
        }

        if len(estado_ids) != len(estados_data):
            raise CommandError(
                "Existen IDs de Estado duplicados."
            )

        if len(municipio_ids) != len(municipios_data):
            raise CommandError(
                "Existen IDs de Municipio duplicados."
            )

        if len(parroquia_ids) != len(parroquias_data):
            raise CommandError(
                "Existen IDs de Parroquia duplicados."
            )

        for item in municipios_data:
            parent_id = (item.get("parent") or {}).get("id")

            if parent_id not in estado_ids:
                raise CommandError(
                    f"Municipio {item.get('id')} "
                    f"referencia un Estado inexistente: {parent_id}"
                )

        for item in parroquias_data:
            parent_id = (item.get("parent") or {}).get("id")

            if parent_id not in municipio_ids:
                raise CommandError(
                    f"Parroquia {item.get('id')} "
                    f"referencia un Municipio inexistente: {parent_id}"
                )

    def _upsert_estados(self, data):
        estados = {}

        for item in data:
            codigo = item["code"]["id"]
            nombre = self._local_name(item)

            estado, _ = Estado.objects.update_or_create(
                codigo=codigo,
                defaults={
                    "nombre": nombre,
                },
            )

            estados[codigo] = estado

        return estados

    def _upsert_municipios(self, data, estados):
        municipios = {}

        for item in data:
            codigo = item["code"]["id"]
            nombre = self._local_name(item)
            estado_codigo = item["parent"]["id"]

            estado = estados.get(estado_codigo)

            if estado is None:
                raise CommandError(
                    f"No se encontró el Estado {estado_codigo} "
                    f"para el Municipio {codigo}."
                )

            municipio, _ = Municipio.objects.update_or_create(
                codigo=codigo,
                defaults={
                    "estado": estado,
                    "nombre": nombre,
                },
            )

            municipios[codigo] = municipio

        return municipios

    def _upsert_parroquias(self, data, municipios):
        for item in data:
            codigo = item["code"]["id"]
            nombre = self._local_name(item)
            municipio_codigo = item["parent"]["id"]

            municipio = municipios.get(municipio_codigo)

            if municipio is None:
                raise CommandError(
                    f"No se encontró el Municipio "
                    f"{municipio_codigo} para la Parroquia {codigo}."
                )

            Parroquia.objects.update_or_create(
                codigo=codigo,
                defaults={
                    "municipio": municipio,
                    "nombre": nombre,
                },
            )

        return len(data)

    @staticmethod
    def _local_name(item):
        name = item.get("name") or {}

        if isinstance(name, dict):
            value = (
                name.get("local")
                or name.get("en")
                or ""
            )
        else:
            value = str(name)

        value = value.strip()

        if not value:
            raise CommandError(
                f"Registro territorial sin nombre: {item.get('id')}"
            )

        return value

    def _show_database_counts(self):
        self.stdout.write("")
        self.stdout.write("===== BASE DE DATOS =====")
        self.stdout.write(
            f"Estados: {Estado.objects.count()}"
        )
        self.stdout.write(
            f"Municipios: {Municipio.objects.count()}"
        )
        self.stdout.write(
            f"Parroquias: {Parroquia.objects.count()}"
        )
