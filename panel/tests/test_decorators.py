"""Tests de permisos del panel."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


Usuario = get_user_model()


class PanelPermissionsTest(TestCase):

    def setUp(self):
        self.url = reverse("panel:dashboard")

    def test_anonimo_redirige_a_login(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/usuarios/login/", resp.url)

    def test_usuario_normal_no_puede_entrar(self):
        user = Usuario.objects.create_user(
            username="normal", email="n@test.com",
            password="Test1234!abc", rol="USUARIO",
        )
        self.client.force_login(user)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 403)

    def test_administrador_puede_entrar(self):
        user = Usuario.objects.create_user(
            username="admin1", email="a@test.com",
            password="Test1234!abc", rol="ADMINISTRADOR",
        )
        self.client.force_login(user)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_coordinador_puede_entrar(self):
        user = Usuario.objects.create_user(
            username="coord", email="c@test.com",
            password="Test1234!abc", rol="COORDINADOR",
        )
        self.client.force_login(user)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_is_staff_puede_entrar(self):
        user = Usuario.objects.create_user(
            username="staff", email="s@test.com",
            password="Test1234!abc", is_staff=True,
        )
        self.client.force_login(user)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_operador_si_puede_entrar(self):
        """
        OPERADOR es un rol operativo. Puede ver el panel pero con permisos
        limitados (ver centros/refugios/vías, crear reportes, editar inventario).
        """
        user = Usuario.objects.create_user(
            username="op", email="op@test.com",
            password="Test1234!abc", rol="OPERADOR",
        )
        self.client.force_login(user)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_operador_no_puede_crear_centro(self):
        """Regla nueva: OPERADOR no puede crear centros (solo ver)."""
        user = Usuario.objects.create_user(
            username="op2", email="op2@test.com",
            password="Test1234!abc", rol="OPERADOR",
        )
        self.client.force_login(user)
        resp = self.client.get(reverse("panel:centros_nuevo"))
        self.assertEqual(resp.status_code, 403)

    def test_voluntario_si_puede_entrar(self):
        """VOLUNTARIO tiene acceso de lectura al panel."""
        user = Usuario.objects.create_user(
            username="vol", email="vol@test.com",
            password="Test1234!abc", rol="VOLUNTARIO",
        )
        self.client.force_login(user)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_usuario_normal_no_puede_entrar(self):
        """USUARIO sin permisos queda bloqueado."""
        user = Usuario.objects.create_user(
            username="user1", email="user1@test.com",
            password="Test1234!abc", rol="USUARIO",
        )
        self.client.force_login(user)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 403)
