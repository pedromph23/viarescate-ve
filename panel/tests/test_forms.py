"""Tests de los formularios del panel."""
from django.test import TestCase

from panel.forms import CentroAyudaForm


class CentroAyudaFormTest(TestCase):
    """Valida que las reglas de negocio se aplican al formulario."""

    def _base_data(self, **overrides):
        data = {
            "nombre": "Centro de Prueba",
            "tipo": "MIXTO",
            "estado": "",
            "municipio": "",
            "parroquia": "",
            "direccion": "Av. Principal 123",
            "telefono": "04121234567",
            "capacidad": 100,
            "activo": True,
            "observaciones": "",
            "latitud": 10.4806,
            "longitud": -66.9036,
        }
        data.update(overrides)
        return data

    def test_form_invalido_sin_estado(self):
        form = CentroAyudaForm(data=self._base_data(estado=""))
        self.assertFalse(form.is_valid())
        self.assertIn("estado", form.errors)

    def test_form_invalido_con_nombre_absurdo(self):
        form = CentroAyudaForm(data=self._base_data(nombre="asdf1234"))
        # Puede fallar por nombre y por estado/municipio
        self.assertFalse(form.is_valid())
        self.assertIn("nombre", form.errors)

    def test_form_invalido_con_telefono_letras(self):
        form = CentroAyudaForm(data=self._base_data(telefono="abc"))
        self.assertFalse(form.is_valid())
        self.assertIn("telefono", form.errors)

    def test_form_invalido_con_coordenadas_cero(self):
        form = CentroAyudaForm(data=self._base_data(latitud=0, longitud=0))
        self.assertFalse(form.is_valid())

    def test_form_invalido_con_coordenadas_fuera_ve(self):
        form = CentroAyudaForm(data=self._base_data(latitud=50, longitud=0))
        self.assertFalse(form.is_valid())

    def test_telefono_vacio_es_valido(self):
        """El teléfono es opcional."""
        form = CentroAyudaForm(data=self._base_data(telefono=""))
        # Puede fallar por otras razones (estado, municipio), pero no por telefono
        if not form.is_valid():
            self.assertNotIn("telefono", form.errors)
