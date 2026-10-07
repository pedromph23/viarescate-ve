from django.contrib.gis.geos import LineString, Point
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import RequestFactory, TestCase

from core.models import Estado, Municipio, Parroquia
from operaciones.models import (
    AuditLog,
    CentroAyuda,
    Inventario,
    Mision,
    Recurso,
    ReporteVial,
    Refugio,
    Via,
)
from operaciones.services import AuditService


class OperacionesModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.estado = Estado.objects.create(
            codigo="VE01",
            nombre="Estado de Prueba",
        )

        cls.municipio = Municipio.objects.create(
            estado=cls.estado,
            nombre="Municipio de Prueba",
        )

        cls.parroquia = Parroquia.objects.create(
            municipio=cls.municipio,
            nombre="Parroquia de Prueba",
        )

        cls.estado_2 = Estado.objects.create(
            codigo="VE02",
            nombre="Segundo Estado",
        )

        cls.municipio_2 = Municipio.objects.create(
            estado=cls.estado_2,
            nombre="Segundo Municipio",
        )

    def test_centro_ayuda_usa_srid_4326(self):
        centro = CentroAyuda(
            nombre="Centro de Prueba",
            estado=self.estado,
            municipio=self.municipio,
            parroquia=self.parroquia,
            ubicacion=Point(-66.9036, 10.4806, srid=4326),
        )

        centro.full_clean()
        centro.save()

        self.assertEqual(centro.ubicacion.srid, 4326)

    def test_refugio_rechaza_ocupacion_superior_a_capacidad(self):
        refugio = Refugio(
            nombre="Refugio de Prueba",
            estado=self.estado,
            municipio=self.municipio,
            parroquia=self.parroquia,
            ubicacion=Point(-66.9036, 10.4806, srid=4326),
            capacidad=100,
            ocupacion=101,
        )

        with self.assertRaises(ValidationError):
            refugio.full_clean()

    def test_refugio_acepta_ocupacion_valida(self):
        refugio = Refugio(
            nombre="Refugio Válido",
            estado=self.estado,
            municipio=self.municipio,
            parroquia=self.parroquia,
            ubicacion=Point(-66.9036, 10.4806, srid=4326),
            capacidad=100,
            ocupacion=50,
        )

        refugio.full_clean()

    def test_integridad_territorial_municipio(self):
        centro = CentroAyuda(
            nombre="Centro Inconsistente",
            estado=self.estado,
            municipio=self.municipio_2,
            parroquia=self.parroquia,
            ubicacion=Point(-66.9036, 10.4806, srid=4326),
        )

        with self.assertRaises(ValidationError) as context:
            centro.full_clean()

        self.assertIn("municipio", context.exception.message_dict)

    def test_integridad_territorial_parroquia(self):
        parroquia_otro_municipio = Parroquia.objects.create(
            municipio=self.municipio_2,
            nombre="Parroquia Incompatible",
        )

        centro = CentroAyuda(
            nombre="Centro Inconsistente",
            estado=self.estado,
            municipio=self.municipio,
            parroquia=parroquia_otro_municipio,
            ubicacion=Point(-66.9036, 10.4806, srid=4326),
        )

        with self.assertRaises(ValidationError) as context:
            centro.full_clean()

        self.assertIn("parroquia", context.exception.message_dict)

    def test_integridad_territorial_refugio(self):
        refugio = Refugio(
            nombre="Refugio Inconsistente",
            estado=self.estado,
            municipio=self.municipio_2,
            parroquia=self.parroquia,
            ubicacion=Point(-66.9036, 10.4806, srid=4326),
        )

        with self.assertRaises(ValidationError) as context:
            refugio.full_clean()

        self.assertIn("municipio", context.exception.message_dict)

    def test_mision_prioridad_debe_estar_entre_1_y_5(self):
        mision = Mision(
            codigo="MIS-001",
            nombre="Misión de Prueba",
            prioridad=6,
            origen=Point(-66.9036, 10.4806, srid=4326),
            destino=Point(-66.9167, 10.5000, srid=4326),
        )

        with self.assertRaises(ValidationError):
            mision.full_clean()

    def test_reporte_vial_severidad_debe_estar_entre_1_y_5(self):
        reporte = ReporteVial(
            tipo=ReporteVial.Tipos.OBSTACULO,
            ubicacion=Point(-66.9036, 10.4806, srid=4326),
            titulo="Reporte de prueba",
            descripcion="Obstáculo de prueba",
            severidad=6,
        )

        with self.assertRaises(ValidationError):
            reporte.full_clean()

    def test_via_usa_linea_srid_4326(self):
        via = Via(
            nombre="Vía de Prueba",
            estado=self.estado,
            geometria=LineString(
                (-66.90, 10.48),
                (-66.91, 10.49),
                srid=4326,
            ),
        )

        via.full_clean()
        via.save()

        self.assertEqual(via.geometria.srid, 4326)

    def test_db_rechaza_refugio_con_ocupacion_superior_a_capacidad(self):
        refugio = Refugio(
            nombre="Refugio DB Inválido",
            estado=self.estado,
            municipio=self.municipio,
            parroquia=self.parroquia,
            ubicacion=Point(-66.9036, 10.4806, srid=4326),
            capacidad=100,
            ocupacion=101,
        )

        with self.assertRaises(IntegrityError):
            with self.captureOnCommitCallbacks(execute=True):
                refugio.save(force_insert=True)

    def test_db_rechaza_reporte_vial_con_severidad_fuera_de_rango(self):
        reporte = ReporteVial(
            tipo=ReporteVial.Tipos.OBSTACULO,
            ubicacion=Point(-66.9036, 10.4806, srid=4326),
            titulo="Reporte DB inválido",
            descripcion="Severidad fuera del rango permitido",
            severidad=6,
        )

        with self.assertRaises(IntegrityError):
            reporte.save(force_insert=True)

    def test_db_rechaza_mision_con_prioridad_fuera_de_rango(self):
        mision = Mision(
            codigo="MIS-DB-001",
            nombre="Misión DB inválida",
            prioridad=6,
            origen=Point(-66.9036, 10.4806, srid=4326),
            destino=Point(-66.9167, 10.5000, srid=4326),
        )

        with self.assertRaises(IntegrityError):
            mision.save(force_insert=True)

    def test_inventario_no_permite_dos_registros_para_mismo_recurso_y_centro(self):
        centro = CentroAyuda.objects.create(
            nombre="Centro Inventario",
            estado=self.estado,
            municipio=self.municipio,
            parroquia=self.parroquia,
            ubicacion=Point(-66.9036, 10.4806, srid=4326),
        )

        recurso = Recurso.objects.create(
            nombre="Agua potable",
            unidad="litro",
        )

        Inventario.objects.create(
            centro=centro,
            recurso=recurso,
            cantidad=100,
        )

        with self.assertRaises(IntegrityError):
            Inventario.objects.create(
                centro=centro,
                recurso=recurso,
                cantidad=50,
            )


class AuditServiceTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.estado = Estado.objects.create(
            codigo="AU01",
            nombre="Estado Auditoría",
        )

        cls.municipio = Municipio.objects.create(
            estado=cls.estado,
            nombre="Municipio Auditoría",
        )

        cls.parroquia = Parroquia.objects.create(
            municipio=cls.municipio,
            nombre="Parroquia Auditoría",
        )

    def setUp(self):
        self.factory = RequestFactory()
        self.user_model = get_user_model()

        self.usuario = self.user_model.objects.create_user(
            username="auditor",
            email="auditor@example.com",
            password="test-password",
        )

        self.centro = CentroAyuda.objects.create(
            nombre="Centro Auditado",
            estado=self.estado,
            municipio=self.municipio,
            parroquia=self.parroquia,
            ubicacion=Point(-66.9036, 10.4806, srid=4326),
        )

    def test_registra_accion_con_usuario_ip_y_objeto(self):
        request = self.factory.post(
            "/admin/operaciones/centroayuda/add/",
            REMOTE_ADDR="192.168.1.20",
        )
        request.user = self.usuario

        log = AuditService.log(
            request=request,
            accion="CREAR",
            modulo="centros_ayuda",
            objeto=self.centro,
            detalles={"nombre": self.centro.nombre},
        )

        self.assertEqual(log.usuario, self.usuario)
        self.assertEqual(log.ip, "192.168.1.20")
        self.assertEqual(log.accion, "CREAR")
        self.assertEqual(log.modulo, "centros_ayuda")
        self.assertEqual(log.objeto_tipo, "CentroAyuda")
        self.assertEqual(log.objeto_id, str(self.centro.pk))
        self.assertEqual(log.detalles["nombre"], self.centro.nombre)
        self.assertEqual(log.resultado, AuditLog.Resultados.EXITO)

    def test_registra_accion_sin_request(self):
        log = AuditService.log(
            accion="SISTEMA",
            modulo="pruebas",
        )

        self.assertIsNone(log.usuario)
        self.assertIsNone(log.ip)
        self.assertEqual(log.objeto_tipo, "N/A")
        self.assertEqual(log.objeto_id, "N/A")

    def test_registra_resultado_rechazado(self):
        log = AuditService.log(
            accion="CAMBIAR_ESTADO",
            modulo="centros_ayuda",
            objeto=self.centro,
            resultado=AuditService.RESULTADO_RECHAZADO,
            detalles={"motivo": "Prueba de rechazo"},
        )

        self.assertEqual(
            log.resultado,
            AuditLog.Resultados.RECHAZADO,
        )
        self.assertEqual(
            log.detalles["motivo"],
            "Prueba de rechazo",
        )

    def test_prioriza_primera_ip_de_forwarded_for(self):
        request = self.factory.get(
            "/",
            HTTP_X_FORWARDED_FOR="203.0.113.10, 10.0.0.1",
            REMOTE_ADDR="10.0.0.2",
        )

        self.assertEqual(
            AuditService.get_client_ip(request),
            "203.0.113.10",
        )

    def test_usa_remote_addr_si_no_hay_forwarded_for(self):
        request = self.factory.get(
            "/",
            REMOTE_ADDR="10.0.0.5",
        )

        self.assertEqual(
            AuditService.get_client_ip(request),
            "10.0.0.5",
        )
