"""Formulario de reportes viales con mapa y upload de fotos."""
from django import forms
from django.contrib.gis.geos import Point
from django.utils import timezone

from core import messages as msg
from core.validators import validar_coordenadas_ve, validar_imagen_archivo
from operaciones.models import ReporteVial


class ReporteVialForm(forms.ModelForm):
    """Formulario completo para crear/editar reportes viales."""

    # Campos auxiliares para el mapa (no están en el modelo)
    latitud = forms.FloatField(
        min_value=0.6, max_value=12.3, label="Latitud",
        widget=forms.NumberInput(attrs={
            "step": "0.000001",
            "readonly": "readonly",
            "data-validator": "coordenada_lat",
            "id": "id_latitud",
            "class": "coord-readonly",
        }),
    )
    longitud = forms.FloatField(
        min_value=-73.4, max_value=-59.8, label="Longitud",
        widget=forms.NumberInput(attrs={
            "step": "0.000001",
            "readonly": "readonly",
            "data-validator": "coordenada_lng",
            "id": "id_longitud",
            "class": "coord-readonly",
        }),
    )

    class Meta:
        model = ReporteVial
        fields = [
            "tipo",
            "via",
            "titulo",
            "descripcion",
            "severidad",
            "afecta_transito",
            "fecha_incidente",
            "foto",
        ]
        widgets = {
            "tipo": forms.Select(attrs={"data-validator": "codigo", "required": "required"}),
            "via": forms.Select(attrs={"data-validator": "codigo"}),
            "titulo": forms.TextInput(attrs={
                "placeholder": "Ej: Derrumbe en la Panamericana sentido oeste",
                "data-validator": "nombre",
                "minlength": "5",
                "maxlength": "180",
            }),
            "descripcion": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Describa el incidente: qué ocurrió, condiciones, riesgos...",
                "minlength": "10",
                "maxlength": "2000",
            }),
            "severidad": forms.NumberInput(attrs={
                "data-validator": "entero_positivo",
                "min": "1", "max": "5", "inputmode": "numeric",
            }),
            "afecta_transito": forms.CheckboxInput(attrs={
                "class": "panel-toggle",
            }),
            "fecha_incidente": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "data-validator": "fecha_pasada_valida",
                },
                format="%Y-%m-%dT%H:%M",
            ),
            "foto": forms.ClearableFileInput(attrs={
                "accept": "image/jpeg,image/png,image/webp",
                "class": "file-input",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fecha_incidente"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["via"].required = False
        self.fields["via"].empty_label = "— Sin vía específica —"

        # Si estamos editando, cargar lat/lng del PointField
        if self.instance and self.instance.pk and self.instance.ubicacion:
            self.fields["latitud"].initial = self.instance.ubicacion.y
            self.fields["longitud"].initial = self.instance.ubicacion.x

        # Si es creación nueva, fecha_incidente por defecto = ahora
        if not self.instance.pk:
            self.fields["fecha_incidente"].initial = timezone.localtime()

    def clean_titulo(self):
        valor = self.cleaned_data.get("titulo", "").strip()
        if len(valor) < 5:
            raise forms.ValidationError("El título debe tener al menos 5 caracteres.")
        return valor

    def clean_descripcion(self):
        valor = self.cleaned_data.get("descripcion", "").strip()
        if len(valor) < 10:
            raise forms.ValidationError("La descripción debe tener al menos 10 caracteres.")
        return valor

    def clean_foto(self):
        archivo = self.cleaned_data.get("foto")
        if not archivo:
            return None
        # Si es un archivo nuevo (no un valor ya guardado)
        if hasattr(archivo, "size"):
            return validar_imagen_archivo(archivo)
        return archivo

    def clean_fecha_incidente(self):
        from core.validators import validar_fecha_con_referencia
        # Admin puede cargar histórico hasta 1 año en el pasado
        return validar_fecha_con_referencia(
            self.cleaned_data.get("fecha_incidente"),
            referencia=None,
            grace_minutos=10,          # tolerancia un poco mayor para admins
            max_edad_dias=365,         # 1 año para datos históricos
            contexto="incidente",
            permitir_nulo=True,
        )

    def clean(self):
        cleaned = super().clean()
        lat = cleaned.get("latitud")
        lng = cleaned.get("longitud")
        if lat is not None and lng is not None:
            validar_coordenadas_ve(lat, lng)
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        lat = self.cleaned_data["latitud"]
        lng = self.cleaned_data["longitud"]
        instance.ubicacion = Point(lng, lat, srid=4326)
        if commit:
            instance.save()
        return instance
