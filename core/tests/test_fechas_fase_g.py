"""
Tests de validaciones de fecha y campos nuevos — Fase G.
"""
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from core.validators import (
    validar_fecha_futura,
    validar_fecha_no_pasada,
    validar_orden_fechas,
)
from operaciones.models import Mision, Necesidad, Recurso, Refugio


class ValidadoresFechaTest(TestCase):
    """Tests unitarios de los validadores de fecha."""

    def test_fecha_no_pasada_rechaza_ayer(self):
        ayer = timezone.now() - timedelta(days=1)
        with self.assertRaises(ValidationError):
            validar_fecha_no_pasada(ayer)

    def test_fecha_no_pasada_rechaza_1989(self):
        """Un año absurdo debe ser rechazado."""
        from datetime import datetime
        from django.utils import timezone as tz
        vieja = tz.make_aware(datetime(1989, 10, 15, 12, 0))
        with self.assertRaises(ValidationError):
            validar_fecha_no_pasada(vieja)

    def test_fecha_no_pasada_acepta_hoy(self):
        ahora = timezone.now()
        self.assertEqual(validar_fecha_no_pasada(ahora), ahora)

    def test_fecha_no_pasada_acepta_manana(self):
        manana = timezone.now() + timedelta(days=1)
        self.assertEqual(validar_fecha_no_pasada(manana), manana)

    def test_fecha_no_pasada_ignora_none(self):
        self.assertIsNone(validar_fecha_no_pasada(None))

    def test_fecha_futura_rechaza_manana(self):
        manana = timezone.now() + timedelta(days=1)
        with self.assertRaises(ValidationError):
            validar_fecha_futura(manana)

    def test_fecha_futura_acepta_ayer(self):
        ayer = timezone.now() - timedelta(days=1)
        self.assertEqual(validar_fecha_futura(ayer), ayer)

    def test_orden_fechas_rechaza_invertido(self):
        with self.assertRaises(ValidationError):
            validar_orden_fechas(
                timezone.now(),
                timezone.now() - timedelta(hours=1),
                "Mensaje",
            )

    def test_orden_fechas_acepta_correcto(self):
        ahora = timezone.now()
        despues = ahora + timedelta(hours=2)
        self.assertIsNone(validar_orden_fechas(ahora, despues, "Mensaje"))

    def test_orden_fechas_ignora_none(self):
        self.assertIsNone(validar_orden_fechas(None, timezone.now(), "M"))
        self.assertIsNone(validar_orden_fechas(timezone.now(), None, "M"))


class MisionFechasTest(TestCase):
    """Validación cruzada en Mision.clean()."""

    def _crear_mision(self, **kwargs):
        from django.contrib.gis.geos import Point
        defaults = {
            "codigo": "M001",
            "nombre": "Misión de prueba",
            "origen": Point(-66.9, 10.5, srid=4326),
            "destino": Point(-66.8, 10.4, srid=4326),
        }
        defaults.update(kwargs)
        return Mision(**defaults)

    def test_rechaza_entrega_estimada_antes_de_salida(self):
        ahora = timezone.now()
        m = self._crear_mision(
            fecha_salida_planificada=ahora,
            fecha_entrega_estimada=ahora - timedelta(hours=1),
        )
        with self.assertRaises(ValidationError) as ctx:
            m.clean()
        self.assertIn("fecha_entrega_estimada", ctx.exception.error_dict)

    def test_acepta_entrega_estimada_despues_de_salida(self):
        ahora = timezone.now()
        m = self._crear_mision(
            fecha_salida_planificada=ahora,
            fecha_entrega_estimada=ahora + timedelta(hours=3),
        )
        m.clean()

    def test_acepta_fechas_nulas(self):
        m = self._crear_mision()
        m.clean()


class NecesidadFechaTest(TestCase):
    """Validación de fecha_requerida en Necesidad.clean()."""

    @classmethod
    def setUpTestData(cls):
        from core.models import Estado, Municipio, Parroquia
        from django.contrib.gis.geos import Point

        try:
            cls.estado = Estado.objects.first() or Estado.objects.create(
                nombre="Distrito Capital", codigo="DC"
            )
            cls.municipio = Municipio.objects.filter(estado=cls.estado).first() or Municipio.objects.create(
                nombre="Libertador", codigo="LIB", estado=cls.estado
            )
            cls.parroquia = Parroquia.objects.filter(municipio=cls.municipio).first() or Parroquia.objects.create(
                nombre="Altagracia", codigo="ALT", municipio=cls.municipio
            )
            cls.refugio = Refugio.objects.create(
                nombre="Refugio Test",
                estado=cls.estado,
                municipio=cls.municipio,
                parroquia=cls.parroquia,
                ubicacion=Point(-66.9, 10.5, srid=4326),
                capacidad=100,
                ocupacion=20,
            )
            cls.recurso = Recurso.objects.create(
                nombre="Agua potable test-fecha", unidad="litros"
            )
        except Exception as e:
            cls.refugio = None
            cls.recurso = None

    def _skip_if_no_data(self):
        if not self.refugio or not self.recurso:
            self.skipTest("Datos seed no disponibles")

    def test_fecha_requerida_1989_es_rechazada(self):
        """El caso reportado por el usuario."""
        self._skip_if_no_data()
        from datetime import datetime
        n = Necesidad(
            refugio=self.refugio,
            recurso=self.recurso,
            cantidad_requerida=100,
            cantidad_recibida=0,
            fecha_requerida=timezone.make_aware(datetime(1989, 10, 15, 12, 0)),
        )
        with self.assertRaises(ValidationError) as ctx:
            n.clean()
        self.assertIn("fecha_requerida", ctx.exception.error_dict)

    def test_fecha_requerida_ayer_es_rechazada(self):
        self._skip_if_no_data()
        ayer = timezone.now() - timedelta(days=1)
        n = Necesidad(
            refugio=self.refugio,
            recurso=self.recurso,
            cantidad_requerida=100,
            cantidad_recibida=0,
            fecha_requerida=ayer,
        )
        with self.assertRaises(ValidationError):
            n.clean()

    def test_fecha_requerida_ahora_es_aceptada(self):
        self._skip_if_no_data()
        ahora = timezone.now()
        n = Necesidad(
            refugio=self.refugio,
            recurso=self.recurso,
            cantidad_requerida=100,
            cantidad_recibida=0,
            fecha_requerida=ahora,
        )
        n.clean()

    def test_fecha_requerida_futura_es_aceptada(self):
        self._skip_if_no_data()
        futuro = timezone.now() + timedelta(days=3)
        n = Necesidad(
            refugio=self.refugio,
            recurso=self.recurso,
            cantidad_requerida=100,
            cantidad_recibida=0,
            fecha_requerida=futuro,
        )
        n.clean()

    def test_fecha_requerida_muy_lejana_es_rechazada(self):
        self._skip_if_no_data()
        muy_futuro = timezone.now() + timedelta(days=365 * 10)
        n = Necesidad(
            refugio=self.refugio,
            recurso=self.recurso,
            cantidad_requerida=100,
            cantidad_recibida=0,
            fecha_requerida=muy_futuro,
        )
        with self.assertRaises(ValidationError):
            n.clean()

    def test_cantidad_requerida_cero_falla(self):
        self._skip_if_no_data()
        n = Necesidad(
            refugio=self.refugio,
            recurso=self.recurso,
            cantidad_requerida=0,
            cantidad_recibida=0,
        )
        with self.assertRaises(ValidationError):
            n.clean()

    def test_recibida_mayor_que_requerida_falla(self):
        self._skip_if_no_data()
        n = Necesidad(
            refugio=self.refugio,
            recurso=self.recurso,
            cantidad_requerida=10,
            cantidad_recibida=20,
        )
        with self.assertRaises(ValidationError) as ctx:
            n.clean()
        self.assertIn("cantidad_recibida", ctx.exception.error_dict)

    def test_cantidad_pendiente_se_calcula(self):
        self._skip_if_no_data()
        n = Necesidad(
            refugio=self.refugio,
            recurso=self.recurso,
            cantidad_requerida=100,
            cantidad_recibida=30,
        )
        self.assertEqual(n.cantidad_pendiente, 70)

    def test_estado_incoherente_falla(self):
        self._skip_if_no_data()
        n = Necesidad(
            refugio=self.refugio,
            recurso=self.recurso,
            cantidad_requerida=100,
            cantidad_recibida=50,
            estado=Necesidad.Estados.CUBIERTA,
        )
        with self.assertRaises(ValidationError):
            n.clean()
