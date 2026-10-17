"""Formularios del panel con validación centralizada — VíaRescate VE."""
from django import forms
from django.contrib.gis.geos import Point

from core import messages as msg
from core.validators import (
    normalizar_telefono_ve,
    validar_coordenadas_ve,
    validar_nombre_propio,
)
from operaciones.models import CentroAyuda, Mision, Refugio


class CentroAyudaForm(forms.ModelForm):
    latitud = forms.FloatField(
        min_value=0.6, max_value=12.3, label="Latitud",
        widget=forms.NumberInput(attrs={
            "step": "0.000001",
            "readonly": "readonly",
            "data-validator": "coordenada_lat",
            "min": "0.6",
            "max": "12.3",
            "id": "id_latitud",
            "class": "coord-readonly",
        }),
        help_text="Se actualiza al mover el pin en el mapa.",
    )
    longitud = forms.FloatField(
        min_value=-73.4, max_value=-59.8, label="Longitud",
        widget=forms.NumberInput(attrs={
            "step": "0.000001",
            "readonly": "readonly",
            "data-validator": "coordenada_lng",
            "min": "-73.4",
            "max": "-59.8",
            "id": "id_longitud",
            "class": "coord-readonly",
        }),
        help_text="Se actualiza al mover el pin en el mapa.",
    )

    class Meta:
        model = CentroAyuda
        fields = [
            "nombre", "tipo", "estado", "municipio", "parroquia",
            "direccion", "telefono", "capacidad", "activo", "observaciones",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={
                "placeholder": "Ej: Centro de Acopio Central",
                "data-validator": "nombre",
                "minlength": "3",
                "maxlength": "120",
                "autocomplete": "organization",
            }),
            "direccion": forms.TextInput(attrs={
                "placeholder": "Av. Principal, sector...",
                "maxlength": "250",
            }),
            "telefono": forms.TextInput(attrs={
                "placeholder": "+584121234567",
                "data-validator": "telefono",
                "inputmode": "tel",
                "autocomplete": "tel",
            }),
            "capacidad": forms.NumberInput(attrs={
                "data-validator": "entero_positivo",
                "min": "0",
                "max": "1000000",
                "inputmode": "numeric",
            }),
            "observaciones": forms.Textarea(attrs={
                "rows": 3,
                "maxlength": "1000",
                "placeholder": "Notas adicionales (opcional)",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.ubicacion:
            self.fields["latitud"].initial = self.instance.ubicacion.y
            self.fields["longitud"].initial = self.instance.ubicacion.x

    def clean_nombre(self):
        return validar_nombre_propio(self.cleaned_data["nombre"])

    def clean_telefono(self):
        valor = self.cleaned_data.get("telefono", "").strip()
        if not valor:
            return ""
        return normalizar_telefono_ve(valor)

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


class RefugioForm(forms.ModelForm):
    latitud = forms.FloatField(
        min_value=0.6, max_value=12.3, label="Latitud",
        widget=forms.NumberInput(attrs={
            "step": "0.000001", "placeholder": "10.480600",
            "data-validator": "coordenada_lat",
            "min": "0.6", "max": "12.3", "inputmode": "decimal",
        }),
    )
    longitud = forms.FloatField(
        min_value=-73.4, max_value=-59.8, label="Longitud",
        widget=forms.NumberInput(attrs={
            "step": "0.000001", "placeholder": "-66.903600",
            "data-validator": "coordenada_lng",
            "min": "-73.4", "max": "-59.8", "inputmode": "decimal",
        }),
    )

    class Meta:
        model = Refugio
        fields = [
            "nombre", "estado", "municipio", "parroquia",
            "direccion", "telefono", "capacidad", "ocupacion",
            "estado_operativo", "activo", "observaciones",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={
                "placeholder": "Ej: Refugio Bolivariano",
                "data-validator": "nombre",
                "minlength": "3", "maxlength": "120",
            }),
            "direccion": forms.TextInput(attrs={
                "placeholder": "Av. Principal, sector...",
                "maxlength": "250",
            }),
            "telefono": forms.TextInput(attrs={
                "placeholder": "+584121234567",
                "data-validator": "telefono",
                "inputmode": "tel",
            }),
            "capacidad": forms.NumberInput(attrs={
                "data-validator": "entero_positivo",
                "min": "0", "max": "1000000", "inputmode": "numeric",
            }),
            "ocupacion": forms.NumberInput(attrs={
                "data-validator": "entero_positivo",
                "min": "0", "max": "1000000", "inputmode": "numeric",
            }),
            "observaciones": forms.Textarea(attrs={
                "rows": 3, "maxlength": "1000",
                "placeholder": "Notas adicionales (opcional)",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.ubicacion:
            self.fields["latitud"].initial = self.instance.ubicacion.y
            self.fields["longitud"].initial = self.instance.ubicacion.x

    def clean_nombre(self):
        return validar_nombre_propio(self.cleaned_data["nombre"])

    def clean_telefono(self):
        valor = self.cleaned_data.get("telefono", "").strip()
        if not valor:
            return ""
        return normalizar_telefono_ve(valor)

    def clean(self):
        cleaned = super().clean()
        cap = cleaned.get("capacidad")
        ocu = cleaned.get("ocupacion")
        if cap is not None and ocu is not None and ocu > cap:
            self.add_error("ocupacion", msg.OCUPACION_MAYOR_CAPACIDAD)
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


class MisionForm(forms.ModelForm):
    """Formulario de Misión con fechas editables."""

    class Meta:
        model = Mision
        fields = [
            "codigo", "nombre", "descripcion",
            "estado_mision", "modo_ruta", "prioridad",
            "vehiculo", "coordinador",
            "fecha_salida_planificada", "fecha_entrega_estimada",
            "observaciones",
        ]
        widgets = {
            "codigo": forms.TextInput(attrs={
                "placeholder": "Ej: MIS_001",
                "data-validator": "codigo",
                "pattern": "[A-Z][A-Z0-9_]{2,29}",
                "maxlength": "40",
                "style": "text-transform: uppercase;",
            }),
            "nombre": forms.TextInput(attrs={
                "placeholder": "Nombre de la misión",
                "data-validator": "nombre",
                "maxlength": "180",
            }),
            "fecha_salida_planificada": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "data-validator": "fecha_futura",
                },
                format="%Y-%m-%dT%H:%M",
            ),
            "fecha_entrega_estimada": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "data-validator": "fecha_futura",
                },
                format="%Y-%m-%dT%H:%M",
            ),
            "descripcion": forms.Textarea(attrs={"rows": 3, "maxlength": "1000"}),
            "observaciones": forms.Textarea(attrs={"rows": 3, "maxlength": "1000"}),
            "prioridad": forms.NumberInput(attrs={
                "data-validator": "entero_positivo",
                "min": "1", "max": "5", "inputmode": "numeric",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in ("fecha_salida_planificada", "fecha_entrega_estimada"):
            self.fields[f].input_formats = ["%Y-%m-%dT%H:%M"]
