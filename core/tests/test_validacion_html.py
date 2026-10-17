"""
Tests de validación HTML5 y atributos de accesibilidad en los forms del panel.
Verifican que los formularios rendericen los atributos esperados:
- data-validator (para JS cliente)
- pattern, min, max, maxlength (HTML5 nativo)
- inputmode, autocomplete (mobile UX)
- required, aria-label
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from panel.forms import CentroAyudaForm, RefugioForm
from panel.forms_necesidad import NecesidadForm


Usuario = get_user_model()


class HTML5AttributesFormTest(TestCase):
    """Verifica que los forms declaren los atributos HTML5 correctos."""

    def test_centro_nombre_tiene_validacion(self):
        """El campo nombre debe tener data-validator + minlength + maxlength."""
        form = CentroAyudaForm()
        widget = form.fields["nombre"].widget
        self.assertEqual(widget.attrs.get("data-validator"), "nombre")
        self.assertEqual(widget.attrs.get("minlength"), "3")
        # El modelo define max_length=180; el form hereda ese valor
        self.assertEqual(str(widget.attrs.get("maxlength")), "180")

    def test_centro_telefono_tiene_validacion(self):
        form = CentroAyudaForm()
        widget = form.fields["telefono"].widget
        self.assertEqual(widget.attrs.get("data-validator"), "telefono")
        self.assertEqual(widget.attrs.get("inputmode"), "tel")
        self.assertEqual(widget.attrs.get("autocomplete"), "tel")

    def test_centro_latitud_tiene_rango_venezuela(self):
        form = CentroAyudaForm()
        widget = form.fields["latitud"].widget
        self.assertEqual(widget.attrs.get("data-validator"), "coordenada_lat")
        # Django normaliza min_value/max_value del field a float
        self.assertEqual(float(widget.attrs.get("min")), 0.6)
        self.assertEqual(float(widget.attrs.get("max")), 12.3)

    def test_centro_longitud_tiene_rango_venezuela(self):
        form = CentroAyudaForm()
        widget = form.fields["longitud"].widget
        self.assertEqual(widget.attrs.get("data-validator"), "coordenada_lng")
        self.assertEqual(float(widget.attrs.get("min")), -73.4)
        self.assertEqual(float(widget.attrs.get("max")), -59.8)

    def test_centro_capacidad_inputmode_numeric(self):
        form = CentroAyudaForm()
        widget = form.fields["capacidad"].widget
        self.assertEqual(widget.attrs.get("data-validator"), "entero_positivo")
        self.assertEqual(widget.attrs.get("inputmode"), "numeric")

    def test_centro_observaciones_maxlength(self):
        form = CentroAyudaForm()
        widget = form.fields["observaciones"].widget
        self.assertEqual(widget.attrs.get("maxlength"), "1000")

    def test_refugio_nombre_validacion(self):
        form = RefugioForm()
        widget = form.fields["nombre"].widget
        self.assertEqual(widget.attrs.get("data-validator"), "nombre")

    def test_refugio_ocupacion_validacion(self):
        form = RefugioForm()
        widget = form.fields["ocupacion"].widget
        self.assertEqual(widget.attrs.get("data-validator"), "entero_positivo")

    def test_necesidad_fecha_validacion_futura(self):
        form = NecesidadForm()
        widget = form.fields["fecha_requerida"].widget
        # Django guarda el type en `input_type`, no en attrs
        self.assertEqual(widget.input_type, "datetime-local")
        self.assertEqual(widget.attrs.get("data-validator"), "fecha_futura")

    def test_necesidad_refugio_required(self):
        form = NecesidadForm()
        widget = form.fields["refugio"].widget
        self.assertEqual(widget.attrs.get("required"), "required")


class FormTemplateRenderTest(TestCase):
    """Verifica que el template HTML renderice los atributos."""

    @classmethod
    def setUpTestData(cls):
        cls.admin = Usuario.objects.create_user(
            username="admin_html_test",
            email="admin_html@test.com",
            password="Test1234!abc",
            rol="ADMINISTRADOR",
            is_staff=True,
        )

    def test_form_centro_renderiza_data_validate(self):
        self.client.force_login(self.admin)
        resp = self.client.get(reverse("panel:centros_nuevo"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'data-validate="true"')
        self.assertContains(resp, 'novalidate')

    def test_form_centro_renderiza_data_validator_nombre(self):
        self.client.force_login(self.admin)
        resp = self.client.get(reverse("panel:centros_nuevo"))
        self.assertContains(resp, 'data-validator="nombre"')
        self.assertContains(resp, 'data-validator="telefono"')
        self.assertContains(resp, 'data-validator="coordenada_lat"')

    def test_form_refugio_renderiza_validadores(self):
        self.client.force_login(self.admin)
        resp = self.client.get(reverse("panel:refugios_nuevo"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'data-validator="nombre"')
        self.assertContains(resp, 'data-validator="entero_positivo"')

    def test_form_necesidad_renderiza_datetime_local(self):
        self.client.force_login(self.admin)
        resp = self.client.get(reverse("panel:necesidades_nueva"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'type="datetime-local"')
        self.assertContains(resp, 'data-validator="fecha_futura"')

    def test_form_incluye_csrf(self):
        self.client.force_login(self.admin)
        resp = self.client.get(reverse("panel:centros_nuevo"))
        self.assertContains(resp, "csrfmiddlewaretoken")


class ValidatorsJsCargadoTest(TestCase):
    """Verifica que validators.js esté referenciado en base.html."""

    def test_validators_js_se_carga(self):
        from django.contrib.staticfiles import finders
        path = finders.find("js/validators.js")
        self.assertIsNotNone(path, "validators.js no está en STATICFILES_DIRS")

        with open(path, "rb") as f:
            content = f.read()
        # Verificaciones clave
        self.assertIn(b"data-validator", content)
        self.assertIn(b"coordenada_lat", content)
        self.assertIn(b"nombre", content)

    def test_validators_js_cargado_en_base(self):
        resp = self.client.get("/")
        self.assertContains(resp, "js/validators.js")
