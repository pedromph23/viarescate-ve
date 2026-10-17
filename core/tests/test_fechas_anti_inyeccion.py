"""
Tests: verificar que NO se pueden inyectar fechas falsas en reportes ni misiones.
"""
from datetime import timedelta

from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from core.validators import (
    validar_fecha_con_referencia,
    validar_fecha_en_pasado_o_ahora,
)
from operaciones.models import Mision, ReporteVial


class ValidadorFechaReferenciaTest(TestCase):
    """Tests del validador centralizado."""

    def test_acepta_fecha_reciente(self):
        ahora = timezone.now()
        hace_1h = ahora - timedelta(hours=1)
        self.assertEqual(
            validar_fecha_con_referencia(hace_1h, grace_minutos=5, max_edad_dias=30),
            hace_1h,
        )

    def test_rechaza_futuro_1_hora(self):
        ahora = timezone.now()
        con_atraso = ahora + timedelta(hours=1)
        with self.assertRaises(ValidationError) as ctx:
            validar_fecha_con_referencia(con_atraso, grace_minutos=5)
        self.assertIn("futuro", str(ctx.exception).lower())

    def test_acepta_futuro_dentro_grace(self):
        ahora = timezone.now()
        hace_2min = ahora + timedelta(minutes=2)  # dentro de grace 5
        # No lanza
        validar_fecha_con_referencia(hace_2min, grace_minutos=5)

    def test_rechaza_pasado_31_dias(self):
        ahora = timezone.now()
        hace_31d = ahora - timedelta(days=31)
        with self.assertRaises(ValidationError) as ctx:
            validar_fecha_con_referencia(hace_31d, max_edad_dias=30)
        self.assertIn("días en el pasado", str(ctx.exception))

    def test_acepta_pasado_29_dias(self):
        ahora = timezone.now()
        hace_29d = ahora - timedelta(days=29)
        validar_fecha_con_referencia(hace_29d, max_edad_dias=30)

    def test_acepta_nulo(self):
        self.assertIsNone(validar_fecha_con_referencia(None))

    def test_rechaza_nulo_si_obligatorio(self):
        with self.assertRaises(ValidationError):
            validar_fecha_con_referencia(None, permitir_nulo=False)

    def test_acepta_aware_y_convierte_naive(self):
        from datetime import datetime
        naive = datetime(2026, 10, 16, 12, 0)
        # No debe fallar
        resultado = validar_fecha_con_referencia(
            naive,
            referencia=timezone.now(),
            max_edad_dias=365,
        )
        self.assertTrue(timezone.is_aware(resultado))


class ValidadorFechaPasadoTest(TestCase):
    """Tests para fechas que NUNCA pueden ser futuras."""

    def test_acepta_pasado(self):
        hace = timezone.now() - timedelta(days=1)
        self.assertEqual(validar_fecha_en_pasado_o_ahora(hace), hace)

    def test_rechaza_futuro(self):
        manana = timezone.now() + timedelta(days=1)
        with self.assertRaises(ValidationError):
            validar_fecha_en_pasado_o_ahora(manana)

    def test_acepta_presente_con_grace(self):
        dentro_grace = timezone.now() + timedelta(minutes=3)
        validar_fecha_en_pasado_o_ahora(dentro_grace, grace_minutos=5)


class ReporteVialAntiInyeccionTest(TestCase):
    """Intenta inyectar fechas falsas vía el modelo."""

    def _nuevo_reporte(self, **kwargs):
        defaults = {
            "tipo": "ACCIDENTE",
            "titulo": "Reporte de prueba",
            "descripcion": "Descripción válida de más de 10 caracteres.",
            "severidad": 3,
            "ubicacion": Point(-66.9, 10.5, srid=4326),
        }
        defaults.update(kwargs)
        return ReporteVial(**defaults)

    def test_rechaza_incidente_en_futuro(self):
        """Un usuario malicioso intenta fechar el incidente en el futuro."""
        futuro = timezone.now() + timedelta(days=2)
        r = self._nuevo_reporte(fecha_incidente=futuro)
        with self.assertRaises(ValidationError) as ctx:
            r.clean()
        self.assertIn("fecha_incidente", ctx.exception.error_dict)

    def test_rechaza_incidente_muy_antiguo(self):
        """Fecha del incidente de hace 6 meses (fuera de ventana)."""
        viejo = timezone.now() - timedelta(days=180)
        r = self._nuevo_reporte(fecha_incidente=viejo)
        with self.assertRaises(ValidationError) as ctx:
            r.clean()
        self.assertIn("fecha_incidente", ctx.exception.error_dict)

    def test_acepta_incidente_hoy_mismo(self):
        """Hoy (cualquier hora desde 00:00) es aceptado."""
        ahora = timezone.now()
        r = self._nuevo_reporte(fecha_incidente=ahora)
        r.clean()  # no debe lanzar

    def test_acepta_incidente_hoy_manana(self):
        """Hoy a las 00:00 también es aceptado (mismo día)."""
        hoy_manana = timezone.now().replace(hour=1, minute=0, second=0, microsecond=0)
        r = self._nuevo_reporte(fecha_incidente=hoy_manana)
        r.clean()  # no debe lanzar

    def test_rechaza_incidente_ayer(self):
        """Ayer es rechazado — regla estricta."""
        ayer = timezone.now() - timedelta(days=1)
        r = self._nuevo_reporte(fecha_incidente=ayer)
        with self.assertRaises(ValidationError) as ctx:
            r.clean()
        self.assertIn("fecha_incidente", ctx.exception.error_dict)

    def test_rechaza_resolucion_en_futuro(self):
        """Alguien marca un reporte como 'resuelto' con fecha futura."""
        r = self._nuevo_reporte()
        r.reportado_en = timezone.now() - timedelta(hours=1)
        r.resuelto_en = timezone.now() + timedelta(days=1)
        with self.assertRaises(ValidationError) as ctx:
            r.clean()
        self.assertIn("resuelto_en", ctx.exception.error_dict)

    def test_rechaza_resolucion_antes_de_reporte(self):
        """Resuelto antes de que se reportara — imposible."""
        r = self._nuevo_reporte()
        r.reportado_en = timezone.now() - timedelta(hours=1)
        r.resuelto_en = timezone.now() - timedelta(days=1)
        with self.assertRaises(ValidationError):
            r.clean()


class MisionAntiInyeccionTest(TestCase):
    """Misiones: fechas reales no pueden ser futuras."""

    def _nueva_mision(self, **kwargs):
        defaults = {
            "codigo": "TEST_ANTI",
            "nombre": "Misión de prueba",
            "origen": Point(-66.9, 10.5, srid=4326),
            "destino": Point(-66.8, 10.4, srid=4326),
        }
        defaults.update(kwargs)
        return Mision(**defaults)

    def test_rechaza_iniciada_en_futuro(self):
        """Alguien intenta marcar la misión como 'iniciada' con fecha futura."""
        m = self._nueva_mision(
            iniciada_en=timezone.now() + timedelta(hours=2),
        )
        with self.assertRaises(ValidationError) as ctx:
            m.clean()
        self.assertIn("iniciada_en", ctx.exception.error_dict)

    def test_rechaza_entregada_en_futuro(self):
        m = self._nueva_mision(
            entregada_en=timezone.now() + timedelta(days=1),
        )
        with self.assertRaises(ValidationError) as ctx:
            m.clean()
        self.assertIn("entregada_en", ctx.exception.error_dict)

    def test_acepta_fechas_realistas(self):
        ahora = timezone.now()
        m = self._nueva_mision(
            iniciada_en=ahora - timedelta(hours=3),
            entregada_en=ahora - timedelta(hours=1),
        )
        m.clean()  # no debe lanzar


class FormPublicoAntiInyeccionTest(TestCase):
    """Verifica que el form público rechace fechas maliciosas."""

    def _data_base(self, **kwargs):
        data = {
            "tipo": "ACCIDENTE",
            "titulo": "Test anti-inyección",
            "descripcion": "Descripción de más de 10 caracteres para pasar validación.",
            "severidad": "3",
            "latitud": "10.5",
            "longitud": "-66.9",
            "afecta_transito": "on",
            "website": "",  # honeypot vacío
        }
        data.update(kwargs)
        return data

    def test_rechaza_fecha_futura(self):
        from operaciones.forms_publico import ReportePublicoForm
        futuro = (timezone.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
        form = ReportePublicoForm(data=self._data_base(fecha_incidente=futuro))
        self.assertFalse(form.is_valid())
        self.assertIn("fecha_incidente", form.errors)

    def test_rechaza_honeypot_lleno(self):
        from operaciones.forms_publico import ReportePublicoForm
        form = ReportePublicoForm(data=self._data_base(website="bot-spam"))
        self.assertFalse(form.is_valid())
        self.assertIn("website", form.errors)
