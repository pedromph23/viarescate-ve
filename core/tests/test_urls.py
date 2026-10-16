"""Tests de rutas — VíaRescate VE."""
from django.test import TestCase
from django.urls import reverse


class AdminHiddenTest(TestCase):
    """/admin/ debe estar bloqueado con 404."""

    def test_admin_clasico_da_404(self):
        resp = self.client.get("/admin/")
        self.assertEqual(resp.status_code, 404)

    def test_admin_login_tambien_404(self):
        resp = self.client.get("/admin/login/")
        self.assertEqual(resp.status_code, 404)


class PanelDjangoRouteTest(TestCase):
    """El admin real está en /panel-django/."""

    def test_panel_django_redirige_a_login(self):
        resp = self.client.get("/panel-django/")
        # Sin sesión redirige al login del admin
        self.assertIn(resp.status_code, (301, 302))


class PanelPublicoRouteTest(TestCase):
    """El panel público está en /administracion/."""

    def test_administracion_redirige_a_login_sin_sesion(self):
        resp = self.client.get("/administracion/")
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/usuarios/login/", resp.url)

    def test_administracion_login_es_la_url_correcta(self):
        # Verifica que la URL existe y resuelve
        url = reverse("panel:dashboard")
        self.assertEqual(url, "/administracion/")


class HealthCheckTest(TestCase):
    def test_health_responde_ok(self):
        resp = self.client.get("/health/")
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(resp.content, {"status": "ok"})


class HomeTest(TestCase):
    def test_home_carga(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)

    def test_home_no_requiere_login(self):
        resp = self.client.get("/")
        self.assertNotEqual(resp.status_code, 302)


class MapaTest(TestCase):
    def test_mapa_publico_accesible(self):
        resp = self.client.get(reverse("mapa:publico"))
        self.assertEqual(resp.status_code, 200)
