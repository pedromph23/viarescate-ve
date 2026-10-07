from django.db import IntegrityError
from django.test import TestCase

from .models import Usuario


class UsuarioModelTests(TestCase):
    def test_usuario_utiliza_uuid_y_rol_por_defecto(self):
        usuario = Usuario.objects.create_user(
            username="usuario.prueba",
            email="usuario@example.com",
            password="ClaveSegura123!",
        )

        self.assertIsNotNone(usuario.id)
        self.assertEqual(usuario.rol, Usuario.Roles.USUARIO)
        self.assertEqual(usuario.email, "usuario@example.com")

    def test_correo_es_unico(self):
        Usuario.objects.create_user(
            username="usuario1",
            email="unico@example.com",
            password="ClaveSegura123!",
        )

        with self.assertRaises(IntegrityError):
            Usuario.objects.create_user(
                username="usuario2",
                email="unico@example.com",
                password="OtraClave123!",
            )
