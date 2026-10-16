"""Tests de validadores centralizados — VíaRescate VE."""
from django.core.exceptions import ValidationError
from django.test import TestCase

from core.validators import (
    normalizar_telefono_ve,
    validar_cantidad,
    validar_cedula_ve,
    validar_codigo_interno,
    validar_coordenadas_ve,
    validar_email,
    validar_nombre_propio,
    validar_placa_ve,
    validar_rif,
)


class NombrePropioTest(TestCase):
    def test_acepta_nombres_normales(self):
        self.assertEqual(validar_nombre_propio("María José"), "María José")
        self.assertEqual(validar_nombre_propio("San Cristóbal"), "San Cristóbal")
        self.assertEqual(validar_nombre_propio("O'Leary"), "O'Leary")
        self.assertEqual(validar_nombre_propio("Centro Norte"), "Centro Norte")

    def test_normaliza_espacios(self):
        self.assertEqual(validar_nombre_propio("  Juan   Pérez  "), "Juan Pérez")

    def test_rechaza_vacio(self):
        with self.assertRaises(ValidationError):
            validar_nombre_propio("")

    def test_rechaza_numeros(self):
        with self.assertRaises(ValidationError):
            validar_nombre_propio("asdf1234")
        with self.assertRaises(ValidationError):
            validar_nombre_propio("Centro 24")

    def test_rechaza_muy_corto(self):
        with self.assertRaises(ValidationError):
            validar_nombre_propio("ab")

    def test_rechaza_muy_largo(self):
        with self.assertRaises(ValidationError):
            validar_nombre_propio("A" * 130 + " B" * 20)

    def test_rechaza_repetidos(self):
        with self.assertRaises(ValidationError):
            validar_nombre_propio("aaaaa")

    def test_rechaza_html(self):
        with self.assertRaises(ValidationError):
            validar_nombre_propio("<b>Hola</b>")

    def test_rechaza_simbolos(self):
        with self.assertRaises(ValidationError):
            validar_nombre_propio("Test@#$")


class TelefonoTest(TestCase):
    def test_normaliza_movil_con_0(self):
        self.assertEqual(normalizar_telefono_ve("04121234567"), "+584121234567")

    def test_normaliza_movil_con_58(self):
        self.assertEqual(normalizar_telefono_ve("584121234567"), "+584121234567")

    def test_normaliza_movil_con_mas_58(self):
        self.assertEqual(normalizar_telefono_ve("+584121234567"), "+584121234567")

    def test_normaliza_con_espacios_y_guiones(self):
        self.assertEqual(normalizar_telefono_ve("0412-123-4567"), "+584121234567")
        self.assertEqual(normalizar_telefono_ve("0412 123 4567"), "+584121234567")

    def test_acepta_prefijos_moviles_validos(self):
        for prefijo in ("412", "414", "416", "424", "426"):
            self.assertEqual(
                normalizar_telefono_ve(f"0{prefijo}1234567"),
                f"+58{prefijo}1234567",
            )

    def test_rechaza_prefijo_invalido(self):
        with self.assertRaises(ValidationError):
            normalizar_telefono_ve("04991234567")

    def test_rechaza_letras(self):
        with self.assertRaises(ValidationError):
            normalizar_telefono_ve("abc")

    def test_rechaza_vacio(self):
        with self.assertRaises(ValidationError):
            normalizar_telefono_ve("")

    def test_rechaza_muy_corto(self):
        with self.assertRaises(ValidationError):
            normalizar_telefono_ve("0412123")


class CedulaTest(TestCase):
    def test_acepta_formatos_validos(self):
        for prefijo in ("V", "E", "J", "P"):
            self.assertEqual(validar_cedula_ve(f"{prefijo}-12345678"),
                             f"{prefijo}-12345678")

    def test_normaliza_a_mayusculas(self):
        self.assertEqual(validar_cedula_ve("v-12345678"), "V-12345678")

    def test_rechaza_sin_prefijo(self):
        with self.assertRaises(ValidationError):
            validar_cedula_ve("12345678")

    def test_rechaza_prefijo_invalido(self):
        with self.assertRaises(ValidationError):
            validar_cedula_ve("X-12345678")

    def test_rechaza_muy_corta(self):
        with self.assertRaises(ValidationError):
            validar_cedula_ve("V-123")

    def test_rechaza_muy_larga(self):
        with self.assertRaises(ValidationError):
            validar_cedula_ve("V-1234567890")


class RifTest(TestCase):
    def test_acepta_rif_valido(self):
        self.assertEqual(validar_rif("J-12345678-9"), "J-12345678-9")

    def test_rechaza_formato_invalido(self):
        with self.assertRaises(ValidationError):
            validar_rif("J-12345678")


class CodigoTest(TestCase):
    def test_acepta_codigos_validos(self):
        self.assertEqual(validar_codigo_interno("CTR_001"), "CTR_001")
        self.assertEqual(validar_codigo_interno("REF_CCS_02"), "REF_CCS_02")

    def test_normaliza_a_mayusculas(self):
        self.assertEqual(validar_codigo_interno("ctr_001"), "CTR_001")

    def test_rechaza_empezando_con_numero(self):
        with self.assertRaises(ValidationError):
            validar_codigo_interno("1ABC")

    def test_rechaza_muy_corto(self):
        with self.assertRaises(ValidationError):
            validar_codigo_interno("AB")


class PlacaTest(TestCase):
    def test_acepta_formatos_venezolanos(self):
        for placa in ("AB123CD", "A123BCD", "1234AB", "AB1234"):
            self.assertEqual(validar_placa_ve(placa), placa)

    def test_normaliza_espacios(self):
        self.assertEqual(validar_placa_ve("AB 123 CD"), "AB123CD")

    def test_rechaza_formato_invalido(self):
        with self.assertRaises(ValidationError):
            validar_placa_ve("ABC")
        with self.assertRaises(ValidationError):
            validar_placa_ve("12345678")


class CoordenadasTest(TestCase):
    def test_acepta_coordenadas_de_venezuela(self):
        # Caracas
        lat, lng = validar_coordenadas_ve(10.4806, -66.9036)
        self.assertEqual(lat, 10.4806)
        self.assertEqual(lng, -66.9036)

    def test_rechaza_fuera_de_venezuela(self):
        # Europa (lat > 12.3)
        with self.assertRaises(ValidationError):
            validar_coordenadas_ve(50.0, -66.0)
        # Pacífico (lng < -73.4)
        with self.assertRaises(ValidationError):
            validar_coordenadas_ve(10.0, -100.0)

    def test_rechaza_cero_cero(self):
        with self.assertRaises(ValidationError):
            validar_coordenadas_ve(0, 0)

    def test_rechaza_no_numericos(self):
        with self.assertRaises(ValidationError):
            validar_coordenadas_ve("abc", "def")


class CantidadTest(TestCase):
    def test_acepta_enteros_positivos(self):
        self.assertEqual(validar_cantidad(0), 0)
        self.assertEqual(validar_cantidad(100), 100)
        self.assertEqual(validar_cantidad("50"), 50)

    def test_rechaza_negativos(self):
        with self.assertRaises(ValidationError):
            validar_cantidad(-5)

    def test_rechaza_muy_grandes(self):
        with self.assertRaises(ValidationError):
            validar_cantidad(2_000_000)


class EmailTest(TestCase):
    def test_acepta_email_valido(self):
        self.assertEqual(validar_email("User@Example.COM"), "user@example.com")

    def test_rechaza_email_invalido(self):
        with self.assertRaises(ValidationError):
            validar_email("no-es-email")
