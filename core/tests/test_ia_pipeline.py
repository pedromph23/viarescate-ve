"""
Tests del pipeline de IA — Fase IA.

Verifican:
1. El comando corre sin errores con/sin datos
2. La lógica de scoring de misiones (BAJO/MEDIO/ALTO/CRITICO)
3. La creación de alertas a partir de predicciones
4. La API REST responde correctamente
"""
from datetime import timedelta
from io import StringIO
from decimal import Decimal

from django.contrib.gis.geos import Point
from django.core.management import call_command
from django.test import TestCase


def _silencioso(*args, **kwargs):
    """Ejecuta el comando capturando su salida."""
    kwargs.setdefault("stdout", StringIO())
    return call_command(*args, **kwargs)
from django.utils import timezone

from operaciones.models import (
    AlertaPredictiva,
    Mision,
    Necesidad,
    PrediccionDemanda,
    PrediccionMision,
    Recurso,
    Refugio,
)


class PipelineIATest(TestCase):
    """Tests del management command `generar_predicciones`."""

    def test_comando_corre_vacio(self):
        """Sin datos, el comando termina sin excepción."""
        _silencioso("generar_predicciones")
        self.assertEqual(PrediccionDemanda.objects.count(), 0)
        self.assertEqual(PrediccionMision.objects.count(), 0)
        self.assertEqual(AlertaPredictiva.objects.count(), 0)

    def test_solo_demanda(self):
        _silencioso("generar_predicciones", solo_demanda=True)

    def test_solo_misiones(self):
        _silencioso("generar_predicciones", solo_misiones=True)

    def test_solo_alertas(self):
        _silencioso("generar_predicciones", solo_alertas=True)

    def test_horizontes(self):
        for h in ("DIAS_7", "DIAS_14", "DIAS_30"):
            _silencioso("generar_predicciones", horizonte=h)


class MisionScoringTest(TestCase):
    """Valida la clasificación de riesgo en misiones."""

    def test_mision_sin_riesgo_es_bajo(self):
        m = Mision.objects.create(
            codigo="RIESGO-BAJO",
            nombre="Misión sin factores de riesgo",
            origen=Point(-66.9, 10.5, srid=4326),
            destino=Point(-66.8, 10.4, srid=4326),
            prioridad=1,
        )
        _silencioso("generar_predicciones", solo_misiones=True)
        pred = PrediccionMision.objects.get(mision=m)
        self.assertEqual(pred.nivel_riesgo, "BAJO")
        self.assertEqual(float(pred.probabilidad_retraso), 15.0)

    def test_mision_vencida_alta_prioridad_es_critico(self):
        """Fecha vencida + prioridad alta + sin vehículo = CRITICO."""
        m = Mision.objects.create(
            codigo="RIESGO-CRITICO",
            nombre="Misión muy retrasada",
            origen=Point(-66.9, 10.5, srid=4326),
            destino=Point(-66.8, 10.4, srid=4326),
            prioridad=5,
            fecha_salida_planificada=timezone.now() - timedelta(days=3),
            fecha_entrega_estimada=timezone.now() - timedelta(days=1),
        )
        _silencioso("generar_predicciones", solo_misiones=True)
        pred = PrediccionMision.objects.get(mision=m)
        self.assertEqual(pred.nivel_riesgo, "CRITICO")
        self.assertGreaterEqual(float(pred.probabilidad_retraso), 85.0)
        self.assertTrue(len(pred.razones) > 0)


class PrediccionDemandaTest(TestCase):
    """Tests de predicción de demanda."""

    @classmethod
    def setUpTestData(cls):
        from core.models import Estado, Municipio, Parroquia

        estado = Estado.objects.first()
        if not estado:
            estado = Estado.objects.create(nombre="Test Estado", codigo="TST")
        municipio = Municipio.objects.filter(estado=estado).first()
        if not municipio:
            municipio = Municipio.objects.create(
                nombre="Test Mun", codigo="TM", estado=estado
            )
        parroquia = Parroquia.objects.filter(municipio=municipio).first()
        if not parroquia:
            parroquia = Parroquia.objects.create(
                nombre="Test Par", codigo="TP", municipio=municipio
            )

        cls.refugio = Refugio.objects.create(
            nombre="Refugio IA Test",
            estado=estado,
            municipio=municipio,
            parroquia=parroquia,
            ubicacion=Point(-66.9, 10.5, srid=4326),
            capacidad=100,
            ocupacion=30,
        )
        cls.recurso = Recurso.objects.create(
            nombre="Recurso IA Test", unidad="kg"
        )

    def test_demanda_se_predice_con_factor_horizonte(self):
        Necesidad.objects.create(
            refugio=self.refugio,
            recurso=self.recurso,
            cantidad_requerida=Decimal("100.00"),
            cantidad_recibida=Decimal("0.00"),
            estado="PENDIENTE",
            fecha_requerida=timezone.now() + timedelta(days=5),
        )

        _silencioso("generar_predicciones", solo_demanda=True, horizonte="DIAS_7")
        p7 = PrediccionDemanda.objects.get(
            refugio=self.refugio, recurso=self.recurso, horizonte="DIAS_7"
        )
        self.assertAlmostEqual(float(p7.cantidad_predicha), 100.0, places=1)

        _silencioso("generar_predicciones", solo_demanda=True, horizonte="DIAS_14")
        p14 = PrediccionDemanda.objects.get(
            refugio=self.refugio, recurso=self.recurso, horizonte="DIAS_14"
        )
        # Factor 1.8 → 180
        self.assertAlmostEqual(float(p14.cantidad_predicha), 180.0, places=1)

    def test_confianza_crece_con_volumen(self):
        Necesidad.objects.create(
            refugio=self.refugio,
            recurso=self.recurso,
            cantidad_requerida=Decimal("500.00"),
            cantidad_recibida=Decimal("0.00"),
            estado="PENDIENTE",
            fecha_requerida=timezone.now() + timedelta(days=3),
        )
        _silencioso("generar_predicciones", solo_demanda=True, horizonte="DIAS_14")
        p = PrediccionDemanda.objects.get(refugio=self.refugio, recurso=self.recurso)
        # Confianza debe ser > 50 con cantidad alta
        self.assertGreater(float(p.confianza), 50.0)
        self.assertLessEqual(float(p.confianza), 85.0)


class AlertasPredictivasTest(TestCase):
    """Verifica la generación de alertas a partir de predicciones."""

    def test_alertas_previas_se_desactivan(self):
        """Cada corrida desactiva las alertas anteriores."""
        AlertaPredictiva.objects.create(
            tipo="DEMANDA_ALTA",
            severidad="ADVERTENCIA",
            titulo="Vieja",
            descripcion="Debería desactivarse",
            activa=True,
        )
        _silencioso("generar_predicciones", solo_alertas=True)
        viejas = AlertaPredictiva.objects.filter(titulo="Vieja", activa=True)
        self.assertEqual(viejas.count(), 0)


class APIPrediccionesTest(TestCase):
    """Tests de los endpoints REST."""

    def test_demanda_list_requiere_auth(self):
        resp = self.client.get("/api/predicciones/demanda/")
        self.assertIn(resp.status_code, (401, 403))

    def test_misiones_list_requiere_auth(self):
        resp = self.client.get("/api/predicciones/misiones/")
        self.assertIn(resp.status_code, (401, 403))

    def test_alertas_list_requiere_auth(self):
        resp = self.client.get("/api/alertas-predictivas/")
        self.assertIn(resp.status_code, (401, 403))
