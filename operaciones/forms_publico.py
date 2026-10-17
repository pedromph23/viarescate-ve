"""Formulario público de reportes (sin login requerido)."""
import logging

from django import forms
from django.contrib.gis.geos import Point
from django.utils import timezone

from core.validators import (
    validar_coordenadas_ve,
    validar_fecha_con_referencia,
    validar_imagen_archivo,
)
from operaciones.models import ReporteVial

logger = logging.getLogger(__name__)


class ReportePublicoForm(forms.ModelForm):
    """Form público — cualquier usuario puede reportar sin cuenta."""

    latitud = forms.FloatField(
        min_value=0.6, max_value=12.3, label="Latitud",
        widget=forms.NumberInput(attrs={
            "step": "0.000001", "readonly": "readonly",
            "data-validator": "coordenada_lat",
            "id": "id_latitud", "class": "coord-readonly",
        }),
    )
    longitud = forms.FloatField(
        min_value=-73.4, max_value=-59.8, label="Longitud",
        widget=forms.NumberInput(attrs={
            "step": "0.000001", "readonly": "readonly",
            "data-validator": "coordenada_lng",
            "id": "id_longitud", "class": "coord-readonly",
        }),
    )

    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "honeypot", "tabindex": "-1",
            "autocomplete": "off", "aria-hidden": "true",
        }),
    )

    class Meta:
        model = ReporteVial
        fields = ["tipo", "titulo", "descripcion", "severidad",
                  "afecta_transito", "fecha_incidente", "foto"]
        widgets = {
            "tipo": forms.Select(attrs={"required": "required"}),
            "titulo": forms.TextInput(attrs={
                "placeholder": "Ej: Derrumbe en la autopista",
                "maxlength": "180", "minlength": "5",
            }),
            "descripcion": forms.Textarea(attrs={
                "rows": 4, "maxlength": "2000", "minlength": "10",
            }),
            "severidad": forms.Select(choices=[
                (1, "1 — Leve"), (2, "2 — Menor"), (3, "3 — Moderado"),
                (4, "4 — Grave"), (5, "5 — Crítico"),
            ]),
            "afecta_transito": forms.CheckboxInput(attrs={"class": "panel-toggle"}),
            "fecha_incidente": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "data-validator": "fecha_pasada_valida",
                    "id": "id_fecha_incidente",
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
        if not self.instance.pk:
            self.fields["fecha_incidente"].initial = timezone.localtime()

    def clean_website(self):
        if self.cleaned_data.get("website", ""):
            raise forms.ValidationError("Reporte rechazado.")
        return ""

    def clean_titulo(self):
        v = self.cleaned_data.get("titulo", "").strip()
        if len(v) < 5:
            raise forms.ValidationError("El título debe tener al menos 5 caracteres.")
        return v

    def clean_descripcion(self):
        v = self.cleaned_data.get("descripcion", "").strip()
        if len(v) < 10:
            raise forms.ValidationError("La descripción debe tener al menos 10 caracteres.")
        return v

    def clean_foto(self):
        archivo = self.cleaned_data.get("foto")
        if archivo and hasattr(archivo, "size"):
            return validar_imagen_archivo(archivo)
        return archivo

    def clean_fecha_incidente(self):
        return validar_fecha_con_referencia(
            self.cleaned_data.get("fecha_incidente"),
            referencia=None,
            grace_minutos=5,
            solo_hoy=True,
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
        instance.estado_reporte = "PENDIENTE"

        if commit:
            # Intentar guardar CON foto primero
            try:
                instance.save()
            except Exception as exc:
                # Si falla por Storage (S3), guardar SIN foto
                logger.error(
                    "Error guardando foto en Storage, se guarda sin foto: %s", exc
                )
                if instance.foto:
                    instance.foto = None
                instance.save()
        return instance
