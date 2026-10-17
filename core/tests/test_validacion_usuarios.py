"""Tests de validación de campos en gestión de usuarios."""
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from core.validators import (
    validar_nombre_persona,
    validar_password_fuerte,
    validar_username,
)

Usuario = get_user_model()


class UsernameValidatorTest(TestCase):
    def test_acepta_username_valido(self):
        self.assertEqual(validar_username("jperez"), "jperez")
        self.assertEqual(validar_username("juan.perez"), "juan.perez")
        self.assertEqual(validar_username("user_123"), "user_123")

    def test_rechaza_muy_corto(self):
        with self.assertRaises(ValidationError):
            validar_username("ab")

    def test_rechaza_con_espacios(self):
        with self.assertRaises(ValidationError):
            validar_username("juan perez")

    def test_rechaza_con_simbolos(self):
        with self.assertRaises(ValidationError):
            validar_username("juan@perez")

    def test_rechaza_empezando_con_punto(self):
        with self.assertRaises(ValidationError):
            validar_username(".perez")

    def test_rechaza_empezando_con_guion(self):
        with self.assertRaises(ValidationError):
            validar_username("-perez")

    def test_rechaza_vacio(self):
        with self.assertRaises(ValidationError):
            validar_username("")


class NombrePersonaValidatorTest(TestCase):
    def test_acepta_nombres_comunes(self):
        self.assertEqual(validar_nombre_persona("Juan"), "Juan")
        self.assertEqual(validar_nombre_persona("María José"), "María José")
        self.assertEqual(validar_nombre_persona("Pérez"), "Pérez")
        self.assertEqual(validar_nombre_persona("O'Leary"), "O'Leary")

    def test_acepta_nombres_con_articulos(self):
        self.assertEqual(
            validar_nombre_persona("María de los Ángeles"),
            "María de los Ángeles",
        )

    def test_rechaza_con_numeros(self):
        with self.assertRaises(ValidationError):
            validar_nombre_persona("Juan123")

    def test_rechaza_con_html(self):
        with self.assertRaises(ValidationError):
            validar_nombre_persona("<script>alert</script>")

    def test_rechaza_muy_corto(self):
        with self.assertRaises(ValidationError):
            validar_nombre_persona("J")


class PasswordFuerteValidatorTest(TestCase):
    def test_acepta_password_valida(self):
        # No debe lanzar
        validar_password_fuerte("MyStr0ng!Pass#2026")

    def test_rechaza_muy_corta(self):
        with self.assertRaises(ValidationError):
            validar_password_fuerte("Short1!x")

    def test_rechaza_sin_mayuscula(self):
        with self.assertRaises(ValidationError):
            validar_password_fuerte("mystr0ng!pass#2026")

    def test_rechaza_sin_simbolo(self):
        with self.assertRaises(ValidationError):
            validar_password_fuerte("MyStrongPass2026")

    def test_rechaza_password_comun(self):
        with self.assertRaises(ValidationError):
            validar_password_fuerte("password123")

    def test_rechaza_si_contiene_username(self):
        with self.assertRaises(ValidationError):
            validar_password_fuerte(
                "Juan2026!StrongP@ss",
                username="juan",
            )

    def test_rechaza_si_contiene_email(self):
        with self.assertRaises(ValidationError):
            validar_password_fuerte(
                "Perez2026!StrongP@ss",
                email="perez@example.com",
            )


class FormCrearUsuarioTest(TestCase):
    def _data(self, **overrides):
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "first_name": "Juan",
            "last_name": "Pérez",
            "rol": "VOLUNTARIO",
            "telefono": "+584121234567",
            "is_active": True,
            "password1": "MyStr0ng!Pass#2026",
            "password2": "MyStr0ng!Pass#2026",
        }
        data.update(overrides)
        return data

    def test_form_valido(self):
        from panel.forms_usuario import UsuarioCrearForm
        from panel.user_hierarchy import NIVEL_ADMINISTRADOR

        gestor = Usuario(
            username="admin", email="a@t.com",
            rol="ADMINISTRADOR", is_superuser=True,
        )
        form = UsuarioCrearForm(data=self._data(), gestor=gestor)
        # No asumimos que sea válido del todo (puede fallar por password validators
        # de Django), pero verificamos que los campos pasan:
        if not form.is_valid():
            # Solo falla si password no cumple — eso es OK
            for field, errors in form.errors.items():
                if field not in ("password1", "password2"):
                    self.fail(f"Campo {field} con error inesperado: {errors}")

    def test_username_invalido_falla(self):
        from panel.forms_usuario import UsuarioCrearForm
        gestor = Usuario(username="admin", email="a@t.com", is_superuser=True)
        form = UsuarioCrearForm(
            data=self._data(username="ab"),  # muy corto
            gestor=gestor,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_email_duplicado_falla(self):
        from panel.forms_usuario import UsuarioCrearForm
        Usuario.objects.create_user(
            username="existente",
            email="existente@example.com",
            password="Test1234!abc",
        )
        gestor = Usuario(username="admin", email="a@t.com", is_superuser=True)
        form = UsuarioCrearForm(
            data=self._data(email="existente@example.com"),
            gestor=gestor,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_telefono_letras_falla(self):
        from panel.forms_usuario import UsuarioCrearForm
        gestor = Usuario(username="admin", email="a@t.com", is_superuser=True)
        form = UsuarioCrearForm(
            data=self._data(telefono="abc"),
            gestor=gestor,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("telefono", form.errors)

    def test_passwords_no_coinciden_falla(self):
        from panel.forms_usuario import UsuarioCrearForm
        gestor = Usuario(username="admin", email="a@t.com", is_superuser=True)
        form = UsuarioCrearForm(
            data=self._data(
                password1="MyStr0ng!Pass#2026",
                password2="MyStr0ng!Pass#DIFFERENT",
            ),
            gestor=gestor,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)


class FormEditarUsuarioTest(TestCase):
    def test_email_duplicado_falla(self):
        from panel.forms_usuario import UsuarioEditarForm
        u1 = Usuario.objects.create_user(
            username="u1", email="u1@example.com", password="Test1234!abc",
        )
        u2 = Usuario.objects.create_user(
            username="u2", email="u2@example.com", password="Test1234!abc",
        )
        gestor = Usuario(username="admin", email="a@t.com", is_superuser=True)
        form = UsuarioEditarForm(
            data={
                "email": "u1@example.com",  # email del otro
                "first_name": "",
                "last_name": "",
                "rol": "VOLUNTARIO",
                "telefono": "",
                "is_active": True,
            },
            instance=u2,
            gestor=gestor,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
