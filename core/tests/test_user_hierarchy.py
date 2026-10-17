"""Tests de la jerarquía de usuarios — VíaRescate VE."""
from django.test import TestCase

from panel.user_hierarchy import (
    NIVEL_ADMINISTRADOR,
    NIVEL_COORDINADOR,
    NIVEL_OPERADOR,
    NIVEL_USUARIO,
    NIVEL_VOLUNTARIO,
    nivel_de,
    puede_crear_usuario,
    puede_modificar_usuario,
    puede_eliminar_usuario,
)
from usuarios.models import Usuario


def _u(username, rol="USUARIO", staff=False, superuser=False):
    return Usuario(
        username=username, email=f"{username}@t.com",
        rol=rol, is_staff=staff, is_superuser=superuser,
    )


class NivelTest(TestCase):
    def test_niveles_correctos(self):
        self.assertEqual(nivel_de(_u("a", "USUARIO")), NIVEL_USUARIO)
        self.assertEqual(nivel_de(_u("b", "VOLUNTARIO")), NIVEL_VOLUNTARIO)
        self.assertEqual(nivel_de(_u("c", "OPERADOR")), NIVEL_OPERADOR)
        self.assertEqual(nivel_de(_u("d", "COORDINADOR")), NIVEL_COORDINADOR)
        self.assertEqual(nivel_de(_u("e", "ADMINISTRADOR")), NIVEL_ADMINISTRADOR)
        self.assertGreater(nivel_de(_u("f", "USUARIO", staff=True)), NIVEL_ADMINISTRADOR)
        self.assertGreater(nivel_de(_u("g", superuser=True)), nivel_de(_u("h", staff=True)))


class ModificacionTest(TestCase):
    def test_admin_puede_modificar_operador(self):
        self.assertTrue(puede_modificar_usuario(
            _u("admin", "ADMINISTRADOR"),
            _u("op", "OPERADOR"),
        ))

    def test_admin_NO_puede_modificar_a_otro_admin(self):
        self.assertFalse(puede_modificar_usuario(
            _u("a1", "ADMINISTRADOR"),
            _u("a2", "ADMINISTRADOR"),
        ))

    def test_admin_NO_puede_modificar_staff(self):
        self.assertFalse(puede_modificar_usuario(
            _u("a1", "ADMINISTRADOR"),
            _u("s1", staff=True),
        ))

    def test_superuser_puede_modificar_a_todos(self):
        admin = _u("admin", "ADMINISTRADOR")
        self.assertTrue(puede_modificar_usuario(_u("su", superuser=True), admin))

    def test_nadie_puede_modificarse_a_si_mismo(self):
        a = _u("a", "ADMINISTRADOR")
        self.assertFalse(puede_modificar_usuario(a, a))

    def test_coordinador_no_puede_modificar_admin(self):
        self.assertFalse(puede_modificar_usuario(
            _u("c", "COORDINADOR"),
            _u("a", "ADMINISTRADOR"),
        ))


class CreacionTest(TestCase):
    def test_admin_no_puede_crear_otro_admin(self):
        admin = _u("admin", "ADMINISTRADOR")
        self.assertFalse(puede_crear_usuario(admin, "ADMINISTRADOR"))

    def test_admin_puede_crear_coordinador(self):
        self.assertTrue(puede_crear_usuario(_u("a", "ADMINISTRADOR"), "COORDINADOR"))

    def test_superuser_puede_crear_admin(self):
        self.assertTrue(puede_crear_usuario(_u("su", superuser=True), "ADMINISTRADOR"))

    def test_coordinador_no_puede_crear_admin(self):
        self.assertFalse(puede_crear_usuario(_u("c", "COORDINADOR"), "ADMINISTRADOR"))
