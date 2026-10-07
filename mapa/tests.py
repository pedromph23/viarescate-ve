from django.apps import apps
from django.test import SimpleTestCase


class MapaAppTests(SimpleTestCase):
    def test_aplicacion_mapa_esta_instalada(self):
        config = apps.get_app_config("mapa")
        self.assertEqual(config.name, "mapa")
