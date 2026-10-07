from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import Estado, Municipio, Parroquia


class TerritorioModelTests(TestCase):
    def setUp(self):
        self.estado = Estado.objects.create(
            codigo="VE-DC",
            nombre="Distrito Capital",
        )
        self.municipio = Municipio.objects.create(
            estado=self.estado,
            nombre="Libertador",
        )

    def test_jerarquia_territorial(self):
        parroquia = Parroquia.objects.create(
            municipio=self.municipio,
            nombre="Altagracia",
        )

        self.assertEqual(parroquia.municipio.estado, self.estado)
        self.assertEqual(
            str(parroquia),
            "Altagracia, Libertador",
        )

    def test_municipio_no_se_duplica_dentro_del_estado(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Municipio.objects.create(
                    estado=self.estado,
                    nombre="Libertador",
                )

    def test_parroquia_no_se_duplica_dentro_del_municipio(self):
        Parroquia.objects.create(
            municipio=self.municipio,
            nombre="Altagracia",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Parroquia.objects.create(
                    municipio=self.municipio,
                    nombre="Altagracia",
                )
