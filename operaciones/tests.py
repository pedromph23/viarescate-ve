from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import LineString, Point
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from core.models import Estado, Municipio, Parroquia
from operaciones.models import (
    AuditLog,
    CentroAyuda,
    Inventario,
    Mision,
    MovimientoInventario,
    Recurso,
    Refugio,
    ReporteVial,
    Vehiculo,
    Via,
)
from usuarios.models import Usuario
from operaciones.services import AuditService
from mapa.services import misiones_geojson, vehiculos_geojson


class OperacionesAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.estado = Estado.objects.create(nombre="Estado API")
        cls.municipio = Municipio.objects.create(
            codigo="API-MUN-01",
            nombre="Municipio API",
            estado=cls.estado,
        )
        cls.parroquia = Parroquia.objects.create(
            codigo="API-PAR-01",
            nombre="Parroquia API",
            municipio=cls.municipio,
        )

        cls.admin = Usuario.objects.create_user(
            username="admin.api",
            email="admin.api@example.com",
            password="ClaveSegura123!",
            rol=Usuario.Roles.ADMINISTRADOR,
        )

        cls.coordinador = Usuario.objects.create_user(
            username="coordinador.api",
            email="coordinador.api@example.com",
            password="ClaveSegura123!",
            rol=Usuario.Roles.COORDINADOR,
        )

        cls.operador = Usuario.objects.create_user(
            username="operador.api",
            email="operador.api@example.com",
            password="ClaveSegura123!",
            rol=Usuario.Roles.OPERADOR,
        )

        cls.voluntario = Usuario.objects.create_user(
            username="voluntario.api",
            email="voluntario.api@example.com",
            password="ClaveSegura123!",
            rol=Usuario.Roles.VOLUNTARIO,
        )

        cls.usuario = Usuario.objects.create_user(
            username="usuario.api",
            email="usuario.api@example.com",
            password="ClaveSegura123!",
            rol=Usuario.Roles.USUARIO,
        )

        cls.centro = CentroAyuda.objects.create(
            nombre="Centro API",
            tipo=CentroAyuda.Tipos.LOGISTICO,
            estado=cls.estado,
            municipio=cls.municipio,
            parroquia=cls.parroquia,
            ubicacion=Point(-66.90, 10.48, srid=4326),
            capacidad=100,
        )

        cls.refugio = Refugio.objects.create(
            nombre="Refugio API",
            estado=cls.estado,
            municipio=cls.municipio,
            parroquia=cls.parroquia,
            ubicacion=Point(-66.91, 10.49, srid=4326),
            capacidad=100,
            ocupacion=20,
        )

        cls.via = Via.objects.create(
            nombre="Vía API",
            codigo="API-001",
            estado=cls.estado,
            geometria=LineString(
                (-66.90, 10.48),
                (-66.91, 10.49),
                srid=4326,
            ),
            estado_vial=Via.Estados.NORMAL,
        )

        cls.recurso = Recurso.objects.create(
            nombre="Agua API",
            unidad="litros",
        )

        cls.inventario = Inventario.objects.create(
            centro=cls.centro,
            recurso=cls.recurso,
            cantidad=Decimal("100.00"),
            minimo=Decimal("20.00"),
        )

        cls.vehiculo = Vehiculo.objects.create(
            placa="API-001",
            tipo=Vehiculo.Tipos.CAMION,
            estado_operativo=Vehiculo.Estados.DISPONIBLE,
            capacidad_kg=Decimal("5000.00"),
            centro=cls.centro,
        )

    def setUp(self):
        self.client = APIClient()

    def autenticar(self, usuario):
        self.client.force_authenticate(user=usuario)

    # ------------------------------------------------------------------
    # Acceso público
    # ------------------------------------------------------------------

    def test_api_root_es_publico(self):
        response = self.client.get("/api/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listado_centros_es_publico(self):
        response = self.client.get("/api/centros-ayuda/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_listado_refugios_es_publico(self):
        response = self.client.get("/api/refugios/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listado_vias_es_publico(self):
        response = self.client.get("/api/vias/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listado_reportes_viales_es_publico(self):
        response = self.client.get("/api/reportes-viales/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ------------------------------------------------------------------
    # Permisos por rol
    # ------------------------------------------------------------------

    def test_usuario_no_puede_crear_centro(self):
        self.autenticar(self.usuario)

        response = self.client.post(
            "/api/centros-ayuda/",
            {
                "nombre": "Centro no autorizado",
                "tipo": CentroAyuda.Tipos.LOGISTICO,
                "estado": str(self.estado.pk),
                "municipio": str(self.municipio.pk),
                "parroquia": str(self.parroquia.pk),
                "ubicacion": "POINT(-66.90 10.48)",
                "capacidad": 50,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_voluntario_no_puede_crear_centro(self):
        self.autenticar(self.voluntario)

        response = self.client.post(
            "/api/centros-ayuda/",
            {
                "nombre": "Centro no autorizado",
                "tipo": CentroAyuda.Tipos.LOGISTICO,
                "estado": str(self.estado.pk),
                "municipio": str(self.municipio.pk),
                "parroquia": str(self.parroquia.pk),
                "ubicacion": "POINT(-66.90 10.48)",
                "capacidad": 50,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_coordinador_puede_crear_centro(self):
        self.autenticar(self.coordinador)

        response = self.client.post(
            "/api/centros-ayuda/",
            {
                "nombre": "Centro creado por coordinador",
                "tipo": CentroAyuda.Tipos.LOGISTICO,
                "estado": str(self.estado.pk),
                "municipio": str(self.municipio.pk),
                "parroquia": str(self.parroquia.pk),
                "ubicacion": "POINT(-66.92 10.50)",
                "capacidad": 50,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            CentroAyuda.objects.filter(
                nombre="Centro creado por coordinador"
            ).exists()
        )

    def test_admin_puede_eliminar_centro(self):
        centro = CentroAyuda.objects.create(
            nombre="Centro para eliminar",
            tipo=CentroAyuda.Tipos.LOGISTICO,
            estado=self.estado,
            municipio=self.municipio,
            parroquia=self.parroquia,
            ubicacion=Point(-66.93, 10.51, srid=4326),
            capacidad=20,
        )

        self.autenticar(self.admin)

        response = self.client.delete(
            f"/api/centros-ayuda/{centro.pk}/"
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            CentroAyuda.objects.filter(pk=centro.pk).exists()
        )

    def test_coordinador_no_puede_eliminar_centro(self):
        self.autenticar(self.coordinador)

        response = self.client.delete(
            f"/api/centros-ayuda/{self.centro.pk}/"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ------------------------------------------------------------------
    # Reportes viales
    # ------------------------------------------------------------------

    def test_voluntario_puede_crear_reporte_vial(self):
        self.autenticar(self.voluntario)

        response = self.client.post(
            "/api/reportes-viales/",
            {
                "tipo": ReporteVial.Tipos.ACCIDENTE,
                "ubicacion": "POINT(-66.94 10.52)",
                "titulo": "Accidente API",
                "descripcion": "Reporte generado desde prueba API",
                "severidad": 3,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        reporte = ReporteVial.objects.get(
            titulo="Accidente API"
        )

        self.assertEqual(reporte.reportado_por, self.voluntario)

    def test_usuario_no_puede_crear_reporte_vial(self):
        self.autenticar(self.usuario)

        response = self.client.post(
            "/api/reportes-viales/",
            {
                "tipo": ReporteVial.Tipos.ACCIDENTE,
                "ubicacion": "POINT(-66.94 10.52)",
                "titulo": "Reporte no autorizado",
                "descripcion": "No debería crearse",
                "severidad": 3,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reporte_vial_se_marca_resuelto(self):
        reporte = ReporteVial.objects.create(
            tipo=ReporteVial.Tipos.OBSTACULO,
            ubicacion=Point(-66.95, 10.53, srid=4326),
            titulo="Obstáculo API",
            descripcion="Obstáculo pendiente",
            severidad=2,
            reportado_por=self.voluntario,
        )

        self.autenticar(self.operador)

        response = self.client.patch(
            f"/api/reportes-viales/{reporte.pk}/",
            {
                "estado_reporte": ReporteVial.Estados.RESUELTO,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        reporte.refresh_from_db()

        self.assertEqual(
            reporte.estado_reporte,
            ReporteVial.Estados.RESUELTO,
        )
        self.assertIsNotNone(reporte.resuelto_en)

    # ------------------------------------------------------------------
    # Misiones
    # ------------------------------------------------------------------

    def test_mision_no_permite_modificar_estado_directamente(self):
        self.autenticar(self.coordinador)

        mision = Mision.objects.create(
            nombre="Misión protegida",
            origen=Point(-66.90, 10.48, srid=4326),
            destino=Point(-66.91, 10.49, srid=4326),
            coordinador=self.coordinador,
            prioridad=3,
        )

        response = self.client.patch(
            f"/api/misiones/{mision.pk}/",
            {"estado_mision": Mision.Estados.ASIGNADA},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        mision.refresh_from_db()
        self.assertEqual(
            mision.estado_mision,
            Mision.Estados.PLANIFICADA,
        )

    def test_mision_no_permite_modificar_fechas_de_transicion_directamente(self):
        self.autenticar(self.coordinador)

        mision = Mision.objects.create(
            codigo="MIS-TEST-FECHAS",
            nombre="Misión fechas protegidas",
            origen=Point(-66.90, 10.48, srid=4326),
            destino=Point(-66.91, 10.49, srid=4326),
            coordinador=self.coordinador,
            prioridad=3,
        )

        fecha_original = mision.iniciada_en

        response = self.client.patch(
            f"/api/misiones/{mision.pk}/",
            {
                "iniciada_en": "2026-10-07T12:00:00Z",
                "entregada_en": "2026-10-07T13:00:00Z",
                "cancelada_en": "2026-10-07T14:00:00Z",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        mision.refresh_from_db()

        self.assertEqual(mision.iniciada_en, fecha_original)
        self.assertIsNone(mision.entregada_en)
        self.assertIsNone(mision.cancelada_en)

    def test_inventario_no_permite_modificar_cantidad_directamente(self):
        self.autenticar(self.operador)

        response = self.client.patch(
            f"/api/inventario/{self.inventario.pk}/",
            {"cantidad": "50.00"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.inventario.refresh_from_db()
        self.assertEqual(
            self.inventario.cantidad,
            Decimal("100.00"),
        )

    def test_inventario_permite_modificar_minimo(self):
        self.autenticar(self.operador)

        response = self.client.patch(
            f"/api/inventario/{self.inventario.pk}/",
            {"minimo": "30.00"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.inventario.refresh_from_db()
        self.assertEqual(
            self.inventario.minimo,
            Decimal("30.00"),
        )

    def test_mision_genera_codigo_automaticamente(self):
        self.autenticar(self.coordinador)

        response = self.client.post(
            "/api/misiones/",
            {
                "nombre": "Misión API",
                "descripcion": "Prueba de generación de código",
                "estado_mision": Mision.Estados.PLANIFICADA,
                "modo_ruta": Mision.ModosRuta.HUMANITARIA,
                "origen": "POINT(-66.90 10.48)",
                "destino": "POINT(-66.95 10.53)",
                "prioridad": 3,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["codigo"].startswith("MIS-"))

        mision = Mision.objects.get(
            pk=response.data["id"]
        )

        self.assertTrue(mision.codigo.startswith("MIS-"))

    def test_usuario_no_puede_crear_mision(self):
        self.autenticar(self.usuario)

        response = self.client.post(
            "/api/misiones/",
            {
                "nombre": "Misión no autorizada",
                "estado_mision": Mision.Estados.PLANIFICADA,
                "modo_ruta": Mision.ModosRuta.HUMANITARIA,
                "origen": "POINT(-66.90 10.48)",
                "destino": "POINT(-66.95 10.53)",
                "prioridad": 3,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("operaciones.api.views.MissionService.plan_route")
    def test_coordinador_puede_planificar_ruta_de_mision(
        self,
        mock_plan_route,
    ):
        self.autenticar(self.coordinador)

        mision = Mision.objects.create(
            nombre="Misión para planificar ruta",
            origen=Point(-66.90, 10.48, srid=4326),
            destino=Point(-66.91, 10.49, srid=4326),
            coordinador=self.coordinador,
            prioridad=3,
        )

        ruta = LineString(
            (-66.90, 10.48),
            (-66.905, 10.485),
            (-66.91, 10.49),
            srid=4326,
        )

        resultado = type(
            "FakeRouteResult",
            (),
            {
                "geometry": ruta,
                "distance_km": 12.34,
                "duration_minutes": 28,
                "provider": "test",
                "candidates_considered": 2,
            },
        )()

        def planificar_ruta_fake(mission, *, save=True):
            if save:
                mission.ruta = resultado.geometry
                mission.distancia_km = resultado.distance_km
                mission.tiempo_estimado_minutos = resultado.duration_minutes
                mission.save(
                    update_fields=(
                        "ruta",
                        "distancia_km",
                        "tiempo_estimado_minutos",
                    )
                )
            return resultado

        mock_plan_route.side_effect = planificar_ruta_fake

        response = self.client.post(
            f"/api/misiones/{mision.pk}/planificar-ruta/",
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        mock_plan_route.assert_called_once_with(
            mision,
            save=True,
        )

        mision.refresh_from_db()

        self.assertEqual(
            mision.estado_mision,
            Mision.Estados.PLANIFICADA,
        )

        self.assertEqual(
            mision.distancia_km,
            Decimal("12.34"),
        )

        self.assertEqual(
            mision.tiempo_estimado_minutos,
            28,
        )

        self.assertIsNotNone(mision.ruta)

        self.assertEqual(
            response.data["estado_mision"],
            Mision.Estados.PLANIFICADA,
        )

        auditoria = AuditLog.objects.filter(
            accion="PLANIFICAR_RUTA_MISION",
            objeto_id=str(mision.pk),
        ).first()

        self.assertIsNotNone(auditoria)

        self.assertEqual(
            auditoria.usuario,
            self.coordinador,
        )

        self.assertEqual(
            auditoria.modulo,
            "operaciones",
        )

        self.assertEqual(
            auditoria.resultado,
            AuditLog.Resultados.EXITO,
        )

        self.assertEqual(
            auditoria.detalles["provider"],
            "test",
        )

        self.assertEqual(
            auditoria.detalles["distance_km"],
            12.34,
        )

        self.assertEqual(
            auditoria.detalles["duration_minutes"],
            28,
        )

        self.assertEqual(
            auditoria.detalles["candidates_considered"],
            2,
        )

    def test_usuario_no_puede_planificar_ruta_de_mision(self):
        self.autenticar(self.usuario)

        mision = Mision.objects.create(
            nombre="Misión sin autorización",
            origen=Point(-66.90, 10.48, srid=4326),
            destino=Point(-66.91, 10.49, srid=4326),
            coordinador=self.coordinador,
            prioridad=3,
        )

        response = self.client.post(
            f"/api/misiones/{mision.pk}/planificar-ruta/",
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    @patch("operaciones.api.views.MissionService.plan_route")
    def test_planificar_ruta_no_cambia_estado_de_mision(
        self,
        mock_plan_route,
    ):
        self.autenticar(self.coordinador)

        mision = Mision.objects.create(
            nombre="Misión mantiene estado",
            estado_mision=Mision.Estados.ASIGNADA,
            origen=Point(-66.90, 10.48, srid=4326),
            destino=Point(-66.91, 10.49, srid=4326),
            coordinador=self.coordinador,
            prioridad=3,
        )

        resultado = type(
            "FakeRouteResult",
            (),
            {
                "geometry": LineString(
                    (-66.90, 10.48),
                    (-66.91, 10.49),
                    srid=4326,
                ),
                "distance_km": 5.50,
                "duration_minutes": 15,
                "provider": "test",
                "candidates_considered": 1,
            },
        )()

        mock_plan_route.return_value = resultado

        response = self.client.post(
            f"/api/misiones/{mision.pk}/planificar-ruta/",
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        mision.refresh_from_db()

        self.assertEqual(
            mision.estado_mision,
            Mision.Estados.ASIGNADA,
        )

    # ------------------------------------------------------------------
    # Inventario
    # ------------------------------------------------------------------

    def test_operador_puede_registrar_entrada(self):
        self.autenticar(self.operador)

        response = self.client.post(
            "/api/movimientos-inventario/",
            {
                "inventario": str(self.inventario.pk),
                "tipo": MovimientoInventario.Tipos.ENTRADA,
                "cantidad": "25.00",
                "referencia": "ENTRADA-API",
                "observaciones": "Prueba API",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.inventario.refresh_from_db()

        self.assertEqual(
            self.inventario.cantidad,
            Decimal("125.00"),
        )

        self.assertEqual(
            MovimientoInventario.objects.filter(
                inventario=self.inventario,
                referencia="ENTRADA-API",
            ).count(),
            1,
        )

    def test_salida_no_puede_dejar_inventario_negativo(self):
        self.autenticar(self.operador)

        response = self.client.post(
            "/api/movimientos-inventario/",
            {
                "inventario": str(self.inventario.pk),
                "tipo": MovimientoInventario.Tipos.SALIDA,
                "cantidad": "999.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.inventario.refresh_from_db()

        self.assertEqual(
            self.inventario.cantidad,
            Decimal("100.00"),
        )

    def test_usuario_no_puede_registrar_movimiento(self):
        self.autenticar(self.usuario)

        response = self.client.post(
            "/api/movimientos-inventario/",
            {
                "inventario": str(self.inventario.pk),
                "tipo": MovimientoInventario.Tipos.ENTRADA,
                "cantidad": "10.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_movimiento_inventario_es_inmutable(self):
        movimiento = MovimientoInventario.objects.create(
            inventario=self.inventario,
            tipo=MovimientoInventario.Tipos.ENTRADA,
            cantidad=Decimal("10.00"),
            realizado_por=self.operador,
        )

        self.autenticar(self.operador)

        response = self.client.patch(
            f"/api/movimientos-inventario/{movimiento.pk}/",
            {
                "cantidad": "20.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    # ------------------------------------------------------------------
    # Auditoría
    # ------------------------------------------------------------------

    def test_creacion_api_genera_auditoria(self):
        self.autenticar(self.coordinador)

        response = self.client.post(
            "/api/recursos/",
            {
                "nombre": "Recurso auditado",
                "unidad": "unidad",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            AuditLog.objects.filter(
                usuario=self.coordinador,
                accion="CREAR",
                objeto_tipo="Recurso",
                resultado=AuditLog.Resultados.EXITO,
            ).exists()
        )

    def test_auditoria_no_es_publica(self):
        response = self.client.get("/api/auditoria/")

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_usuario_no_puede_consultar_auditoria(self):
        self.autenticar(self.usuario)

        response = self.client.get("/api/auditoria/")

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_coordinador_puede_consultar_auditoria(self):
        AuditLog.objects.create(
            usuario=self.coordinador,
            accion="PRUEBA",
            modulo="operaciones",
            objeto_tipo="Prueba",
            objeto_id="1",
            resultado=AuditLog.Resultados.EXITO,
        )

        self.autenticar(self.coordinador)

        response = self.client.get("/api/auditoria/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    # ------------------------------------------------------------------
    # Filtros
    # ------------------------------------------------------------------

    def test_filtro_refugios_por_estado_operativo(self):
        self.refugio.estado_operativo = Refugio.Estados.COMPLETO
        self.refugio.save(update_fields=("estado_operativo", "actualizado_en"))

        response = self.client.get(
            "/api/refugios/",
            {"estado_operativo": Refugio.Estados.COMPLETO},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filtro_vias_por_estado_vial(self):
        response = self.client.get(
            "/api/vias/",
            {"estado_vial": Via.Estados.NORMAL},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filtro_inventario_bajo_minimo(self):
        self.inventario.cantidad = Decimal("10.00")
        self.inventario.save(update_fields=("cantidad", "actualizado_en"))

        response = self.client.get(
            "/api/inventario/",
            {"bajo_minimo": "true"},
        )
    # ------------------------------------------------------------------
    # Protección de información operacional
    # ------------------------------------------------------------------

    def test_vehiculos_no_son_publicos(self):
        response = self.client.get("/api/vehiculos/")

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_misiones_no_son_publicas(self):
        response = self.client.get("/api/misiones/")

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_inventario_no_es_publico(self):
        response = self.client.get("/api/inventario/")

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_movimientos_inventario_no_son_publicos(self):
        response = self.client.get("/api/movimientos-inventario/")

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_usuario_autenticado_puede_consultar_vehiculos(self):
        self.autenticar(self.usuario)

        response = self.client.get("/api/vehiculos/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_usuario_autenticado_puede_consultar_misiones(self):
        self.autenticar(self.usuario)

        response = self.client.get("/api/misiones/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_usuario_autenticado_puede_consultar_inventario(self):
        self.autenticar(self.usuario)

        response = self.client.get("/api/inventario/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_usuario_autenticado_puede_consultar_movimientos(self):
        self.autenticar(self.usuario)

        response = self.client.get("/api/movimientos-inventario/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

class OperacionesGISServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = Usuario.objects.create_user(
            username="gis.usuario",
            email="gis.usuario@example.com",
            password="ClaveSegura123!",
            rol=Usuario.Roles.USUARIO,
        )

        cls.estado = Estado.objects.create(
            codigo="GIS-VE01",
            nombre="Estado GIS",
        )

        cls.municipio = Municipio.objects.create(
            estado=cls.estado,
            codigo="GIS-MUN-01",
            nombre="Municipio GIS",
        )

        cls.parroquia = Parroquia.objects.create(
            municipio=cls.municipio,
            codigo="GIS-PAR-01",
            nombre="Parroquia GIS",
        )

        cls.centro = CentroAyuda.objects.create(
            nombre="Centro GIS",
            tipo=CentroAyuda.Tipos.LOGISTICO,
            estado=cls.estado,
            municipio=cls.municipio,
            parroquia=cls.parroquia,
            ubicacion=Point(-66.90, 10.48, srid=4326),
            capacidad=100,
        )

    def crear_vehiculo(self, placa, activo=True, ubicacion=None):
        return Vehiculo.objects.create(
            placa=placa,
            tipo=Vehiculo.Tipos.CAMION,
            estado_operativo=Vehiculo.Estados.DISPONIBLE,
            capacidad_kg=Decimal("5000.00"),
            centro=self.centro,
            activo=activo,
            ubicacion=ubicacion,
        )

    def crear_mision(
        self,
        codigo,
        estado=Mision.Estados.PLANIFICADA,
        ruta=None,
    ):
        return Mision.objects.create(
            codigo=codigo,
            nombre=f"Misión {codigo}",
            estado_mision=estado,
            modo_ruta=Mision.ModosRuta.HUMANITARIA,
            origen=Point(-66.90, 10.48, srid=4326),
            destino=Point(-66.95, 10.53, srid=4326),
            prioridad=3,
            ruta=ruta,
        )

    def test_vehiculos_geojson_solo_incluye_activos_con_ubicacion(self):
        visible = self.crear_vehiculo(
            "GIS-001",
            ubicacion=Point(-66.90, 10.48, srid=4326),
        )
        self.crear_vehiculo(
            "GIS-002",
            activo=False,
            ubicacion=Point(-66.91, 10.49, srid=4326),
        )
        self.crear_vehiculo("GIS-003")

        resultado = vehiculos_geojson()

        self.assertEqual(resultado["type"], "FeatureCollection")
        self.assertEqual(len(resultado["features"]), 1)
        self.assertEqual(
            resultado["features"][0]["properties"]["id"],
            str(visible.id),
        )
        self.assertEqual(
            resultado["features"][0]["properties"]["placa"],
            "GIS-001",
        )

    def test_vehiculos_geojson_devuelve_propiedades_operativas(self):
        self.crear_vehiculo(
            "GIS-004",
            ubicacion=Point(-66.92, 10.50, srid=4326),
        )

        resultado = vehiculos_geojson()
        properties = resultado["features"][0]["properties"]

        self.assertEqual(properties["placa"], "GIS-004")
        self.assertEqual(
            properties["tipo_codigo"],
            Vehiculo.Tipos.CAMION,
        )
        self.assertEqual(
            properties["estado_operativo"],
            Vehiculo.Estados.DISPONIBLE,
        )
        self.assertEqual(properties["capacidad_kg"], "5000.00")
        self.assertEqual(properties["centro"], "Centro GIS")

    def test_misiones_geojson_solo_incluye_misiones_activas(self):
        self.crear_mision("MIS-001", Mision.Estados.PLANIFICADA)
        self.crear_mision("MIS-002", Mision.Estados.ASIGNADA)
        self.crear_mision("MIS-003", Mision.Estados.EN_RUTA)
        self.crear_mision("MIS-004", Mision.Estados.ENTREGADA)
        self.crear_mision("MIS-005", Mision.Estados.CANCELADA)

        resultado = misiones_geojson()

        codigos = {
            feature["properties"]["codigo"]
            for feature in resultado["features"]
        }

        self.assertEqual(
            codigos,
            {"MIS-001", "MIS-002", "MIS-003"},
        )

    def test_mision_geojson_sin_ruta_incluye_origen_y_destino(self):
        self.crear_mision("MIS-006")

        resultado = misiones_geojson()
        features = resultado["features"]

        self.assertEqual(len(features), 2)

        puntos = {
            feature["properties"]["punto"]
            for feature in features
        }

        self.assertEqual(puntos, {"origen", "destino"})

        for feature in features:
            self.assertEqual(
                feature["geometry"]["type"],
                "Point",
            )

    def test_mision_geojson_con_ruta_incluye_ruta_origen_y_destino(self):
        ruta = LineString(
            (-66.90, 10.48),
            (-66.92, 10.50),
            (-66.95, 10.53),
            srid=4326,
        )

        self.crear_mision("MIS-007", ruta=ruta)

        resultado = misiones_geojson()
        features = resultado["features"]

        self.assertEqual(len(features), 3)

        geometries = {
            feature["geometry"]["type"]
            for feature in features
        }

        self.assertEqual(
            geometries,
            {"LineString", "Point"},
        )

        puntos = {
            feature["properties"]["punto"]
            for feature in features
            if feature["geometry"]["type"] == "Point"
        }

        self.assertEqual(puntos, {"origen", "destino"})

        rutas = [
            feature
            for feature in features
            if feature["geometry"]["type"] == "LineString"
        ]

        self.assertEqual(len(rutas), 1)
        self.assertEqual(
            rutas[0]["properties"]["geometria_tipo"],
            "ruta",
        )

    def test_geojson_misiones_devuelve_feature_collection(self):
        self.crear_mision("MIS-008")

        resultado = misiones_geojson()

        self.assertEqual(
            resultado["type"],
            "FeatureCollection",
        )

        for feature in resultado["features"]:
            self.assertEqual(feature["type"], "Feature")
            self.assertIn("geometry", feature)
            self.assertIn("properties", feature)

    def test_geojson_operacional_requiere_autenticacion(self):
        client = APIClient()

        response_vehiculos = client.get(
            "/mapa/api/geojson/vehiculos/"
        )
        response_misiones = client.get(
            "/mapa/api/geojson/misiones/"
        )

        self.assertEqual(response_vehiculos.status_code, 302)
        self.assertEqual(response_misiones.status_code, 302)

    def test_geojson_operacional_autenticado(self):
        client = APIClient()

        autenticado = client.login(
            username="gis.usuario",
            password="ClaveSegura123!",
        )

        self.assertTrue(autenticado)

        self.crear_vehiculo(
            "GIS-005",
            ubicacion=Point(-66.93, 10.51, srid=4326),
        )
        self.crear_mision("MIS-009")

        response_vehiculos = client.get(
            "/mapa/api/geojson/vehiculos/"
        )
        response_misiones = client.get(
            "/mapa/api/geojson/misiones/"
        )

        self.assertEqual(response_vehiculos.status_code, 200)
        self.assertEqual(response_misiones.status_code, 200)

        self.assertEqual(
            response_vehiculos.json()["type"],
            "FeatureCollection",
        )
        self.assertEqual(
            response_misiones.json()["type"],
            "FeatureCollection",
        )


class OperacionesModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.estado = Estado.objects.create(
            codigo="VE01",
            nombre="Estado de Prueba",
        )

        cls.municipio = Municipio.objects.create(
            estado=cls.estado,
            codigo="TEST-MUN-01",
            nombre="Municipio de Prueba",
        )

        cls.parroquia = Parroquia.objects.create(
            municipio=cls.municipio,
            codigo="TEST-PAR-01",
            nombre="Parroquia de Prueba",
        )

        cls.estado_2 = Estado.objects.create(
            codigo="VE02",
            nombre="Segundo Estado",
        )

        cls.municipio_2 = Municipio.objects.create(
            estado=cls.estado_2,
            codigo="TEST-MUN-02",
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
            codigo="TEST-PAR-02",
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
            codigo="AUD-MUN-01",
            nombre="Municipio Auditoría",
        )

        cls.parroquia = Parroquia.objects.create(
            municipio=cls.municipio,
            codigo="AUD-PAR-01",
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

    @override_settings(AUDIT_TRUST_PROXY_HEADERS=True)
    def test_prioriza_primera_ip_de_forwarded_for_cuando_proxy_es_confiable(self):
        request = self.factory.get(
            "/",
            HTTP_X_FORWARDED_FOR="203.0.113.10, 10.0.0.1",
            REMOTE_ADDR="10.0.0.2",
        )

        self.assertEqual(
            AuditService.get_client_ip(request),
            "203.0.113.10",
        )

    def test_ignora_forwarded_for_cuando_proxy_no_es_confiable(self):
        request = self.factory.get(
            "/",
            HTTP_X_FORWARDED_FOR="203.0.113.10, 10.0.0.1",
            REMOTE_ADDR="10.0.0.2",
        )

        self.assertEqual(
            AuditService.get_client_ip(request),
            "10.0.0.2",
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


class FakeRouteProvider:
    """Proveedor determinista para probar el motor sin Internet."""

    name = "fake"

    def __init__(self, candidates):
        self.candidates = candidates

    def calculate_routes(
        self,
        origin,
        destination,
        *,
        alternatives=True,
    ):
        return self.candidates


class RouteEvaluatorTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.estado = Estado.objects.create(
            codigo="RT01",
            nombre="Estado Rutas",
        )

    def crear_via(
        self,
        codigo,
        geometria,
        estado_vial=Via.Estados.NORMAL,
    ):
        return Via.objects.create(
            nombre=f"Vía {codigo}",
            codigo=codigo,
            estado=self.estado,
            geometria=geometria,
            estado_vial=estado_vial,
            activa=True,
        )

    def crear_geometria(self, y):
        return LineString(
            (-66.95, y),
            (-66.90, y),
            srid=4326,
        )

    def crear_reporte(
        self,
        via,
        *,
        estado_reporte=ReporteVial.Estados.CONFIRMADO,
        severidad=3,
    ):
        return ReporteVial.objects.create(
            via=via,
            tipo=ReporteVial.Tipos.OBSTACULO,
            estado_reporte=estado_reporte,
            ubicacion=Point(-66.925, 10.50, srid=4326),
            titulo="Obstáculo de prueba",
            descripcion="Reporte generado para pruebas del motor.",
            severidad=severidad,
        )

    def test_via_normal_no_agrega_riesgo(self):
        via = self.crear_via(
            "RT-VIA-001",
            self.crear_geometria(10.50),
            Via.Estados.NORMAL,
        )

        from operaciones.routing.evaluator import RouteEvaluator

        evaluation = RouteEvaluator().evaluate(
            via.geometria,
            distance_meters=1000,
            duration_seconds=600,
        )

        self.assertFalse(evaluation.blocked)
        self.assertEqual(evaluation.risk_score, 0.0)
        self.assertEqual(
            evaluation.via_ids,
            (str(via.id),),
        )

    def test_via_afectada_incrementa_riesgo(self):
        via = self.crear_via(
            "RT-VIA-002",
            self.crear_geometria(10.51),
            Via.Estados.AFECTADA,
        )

        from operaciones.routing.evaluator import RouteEvaluator

        evaluation = RouteEvaluator().evaluate(
            via.geometria,
            distance_meters=1000,
            duration_seconds=600,
        )

        self.assertFalse(evaluation.blocked)
        self.assertEqual(evaluation.risk_score, 35.0)
        self.assertEqual(
            evaluation.via_ids,
            (str(via.id),),
        )

    def test_via_cerrada_bloquea_la_ruta(self):
        via = self.crear_via(
            "RT-VIA-003",
            self.crear_geometria(10.52),
            Via.Estados.CERRADA,
        )

        from operaciones.routing.evaluator import RouteEvaluator

        evaluation = RouteEvaluator().evaluate(
            via.geometria,
            distance_meters=1000,
            duration_seconds=600,
        )

        self.assertTrue(evaluation.blocked)
        self.assertEqual(
            evaluation.via_ids,
            (str(via.id),),
        )

    def test_reporte_confirmado_penaliza_segun_severidad(self):
        via = self.crear_via(
            "RT-VIA-004",
            self.crear_geometria(10.53),
        )
        reporte = self.crear_reporte(
            via,
            estado_reporte=ReporteVial.Estados.CONFIRMADO,
            severidad=4,
        )

        from operaciones.routing.evaluator import RouteEvaluator

        evaluation = RouteEvaluator().evaluate(
            via.geometria,
            distance_meters=1000,
            duration_seconds=600,
        )

        self.assertEqual(evaluation.risk_score, 40.0)
        self.assertEqual(
            evaluation.report_ids,
            (str(reporte.id),),
        )

    def test_reporte_pendiente_aplica_penalizacion_reducida(self):
        via = self.crear_via(
            "RT-VIA-005",
            self.crear_geometria(10.54),
        )
        self.crear_reporte(
            via,
            estado_reporte=ReporteVial.Estados.PENDIENTE,
            severidad=5,
        )

        from operaciones.routing.evaluator import RouteEvaluator

        evaluation = RouteEvaluator().evaluate(
            via.geometria,
            distance_meters=1000,
            duration_seconds=600,
        )

        self.assertEqual(evaluation.risk_score, 20.0)

    def test_reportes_rechazado_y_resuelto_no_penalizan(self):
        via = self.crear_via(
            "RT-VIA-006",
            self.crear_geometria(10.55),
        )

        self.crear_reporte(
            via,
            estado_reporte=ReporteVial.Estados.RECHAZADO,
            severidad=5,
        )
        self.crear_reporte(
            via,
            estado_reporte=ReporteVial.Estados.RESUELTO,
            severidad=5,
        )

        from operaciones.routing.evaluator import RouteEvaluator

        evaluation = RouteEvaluator().evaluate(
            via.geometria,
            distance_meters=1000,
            duration_seconds=600,
        )

        self.assertEqual(evaluation.risk_score, 0.0)


class RouteServiceTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.estado = Estado.objects.create(
            codigo="RS01",
            nombre="Estado Servicio Rutas",
        )

    def crear_mision(
        self,
        codigo,
        *,
        modo=Mision.ModosRuta.HUMANITARIA,
    ):
        return Mision.objects.create(
            codigo=codigo,
            nombre=f"Misión {codigo}",
            modo_ruta=modo,
            origen=Point(-66.96, 10.48, srid=4326),
            destino=Point(-66.89, 10.56, srid=4326),
            prioridad=3,
        )

    @staticmethod
    def crear_candidato(
        y,
        *,
        distancia,
        duracion,
    ):
        from operaciones.routing.base import RouteCandidate

        return RouteCandidate(
            geometry=LineString(
                (-66.95, y),
                (-66.90, y),
                srid=4326,
            ),
            distance_meters=distancia,
            duration_seconds=duracion,
        )

    def test_mas_corta_selecciona_la_menor_distancia(self):
        mission = self.crear_mision(
            "RT-MIS-001",
            modo=Mision.ModosRuta.MAS_CORTA,
        )

        candidatos = [
            self.crear_candidato(
                10.60,
                distancia=5000,
                duracion=600,
            ),
            self.crear_candidato(
                10.61,
                distancia=3000,
                duracion=900,
            ),
        ]

        from operaciones.routing.services import RouteService

        result = RouteService(
            provider=FakeRouteProvider(candidatos),
        ).calculate_for_mission(mission)

        self.assertEqual(result.distance_km, 3.0)
        self.assertEqual(result.duration_minutes, 15)
        self.assertEqual(result.candidates_considered, 2)

    def test_mas_rapida_selecciona_el_menor_tiempo(self):
        mission = self.crear_mision(
            "RT-MIS-002",
            modo=Mision.ModosRuta.MAS_RAPIDA,
        )

        candidatos = [
            self.crear_candidato(
                10.62,
                distancia=3000,
                duracion=900,
            ),
            self.crear_candidato(
                10.63,
                distancia=5000,
                duracion=600,
            ),
        ]

        from operaciones.routing.services import RouteService

        result = RouteService(
            provider=FakeRouteProvider(candidatos),
        ).calculate_for_mission(mission)

        self.assertEqual(result.distance_km, 5.0)
        self.assertEqual(result.duration_minutes, 10)

    def test_mas_segura_prioriza_riesgo_sobre_distancia(self):
        via = Via.objects.create(
            nombre="Vía riesgosa",
            codigo="RS-VIA-001",
            estado=self.estado,
            geometria=LineString(
                (-66.95, 10.64),
                (-66.90, 10.64),
                srid=4326,
            ),
            estado_vial=Via.Estados.CRITICA,
            activa=True,
        )

        mission = self.crear_mision(
            "RT-MIS-003",
            modo=Mision.ModosRuta.MAS_SEGURA,
        )

        candidatos = [
            self.crear_candidato(
                10.64,
                distancia=1000,
                duracion=300,
            ),
            self.crear_candidato(
                10.65,
                distancia=6000,
                duracion=900,
            ),
        ]

        from operaciones.routing.services import RouteService

        result = RouteService(
            provider=FakeRouteProvider(candidatos),
        ).calculate_for_mission(mission)

        self.assertEqual(result.distance_km, 6.0)
        self.assertEqual(result.duration_minutes, 15)

    def test_ruta_cerrada_no_puede_ser_seleccionada(self):
        Via.objects.create(
            nombre="Vía cerrada",
            codigo="RS-VIA-002",
            estado=self.estado,
            geometria=LineString(
                (-66.95, 10.66),
                (-66.90, 10.66),
                srid=4326,
            ),
            estado_vial=Via.Estados.CERRADA,
            activa=True,
        )

        mission = self.crear_mision(
            "RT-MIS-004",
            modo=Mision.ModosRuta.MAS_CORTA,
        )

        candidatos = [
            self.crear_candidato(
                10.66,
                distancia=1000,
                duracion=300,
            ),
            self.crear_candidato(
                10.67,
                distancia=5000,
                duracion=900,
            ),
        ]

        from operaciones.routing.services import RouteService

        result = RouteService(
            provider=FakeRouteProvider(candidatos),
        ).calculate_for_mission(mission)

        self.assertEqual(result.distance_km, 5.0)

    def test_todas_las_rutas_cerradas_lanzan_error(self):
        from operaciones.routing.exceptions import RouteValidationError
        from operaciones.routing.services import RouteService

        Via.objects.create(
            nombre="Vía cerrada A",
            codigo="RS-VIA-003",
            estado=self.estado,
            geometria=LineString(
                (-66.95, 10.68),
                (-66.90, 10.68),
                srid=4326,
            ),
            estado_vial=Via.Estados.CERRADA,
            activa=True,
        )

        Via.objects.create(
            nombre="Vía cerrada B",
            codigo="RS-VIA-004",
            estado=self.estado,
            geometria=LineString(
                (-66.95, 10.69),
                (-66.90, 10.69),
                srid=4326,
            ),
            estado_vial=Via.Estados.CERRADA,
            activa=True,
        )

        mission = self.crear_mision(
            "RT-MIS-005",
            modo=Mision.ModosRuta.HUMANITARIA,
        )

        candidatos = [
            self.crear_candidato(
                10.68,
                distancia=1000,
                duracion=300,
            ),
            self.crear_candidato(
                10.69,
                distancia=2000,
                duracion=500,
            ),
        ]

        with self.assertRaises(RouteValidationError):
            RouteService(
                provider=FakeRouteProvider(candidatos),
            ).calculate_for_mission(mission)

    def test_save_guarda_ruta_distancia_y_tiempo(self):
        mission = self.crear_mision(
            "RT-MIS-006",
            modo=Mision.ModosRuta.MAS_CORTA,
        )

        candidato = self.crear_candidato(
            10.70,
            distancia=4250,
            duracion=725,
        )

        from operaciones.routing.services import RouteService

        result = RouteService(
            provider=FakeRouteProvider([candidato]),
        ).calculate_for_mission(
            mission,
            save=True,
        )

        mission.refresh_from_db()

        self.assertEqual(mission.distancia_km, Decimal("4.25"))
        self.assertEqual(mission.tiempo_estimado_minutos, 12)
        self.assertIsNotNone(mission.ruta)
        self.assertTrue(
            mission.ruta.equals(result.geometry)
        )
