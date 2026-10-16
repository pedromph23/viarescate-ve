"""Formularios del panel con validación centralizada."""
from django import forms
from django.contrib.gis.geos import Point

from core import messages as msg
from core.validators import (
    normalizar_telefono_ve,
    validar_coordenadas_ve,
    validar_nombre_propio,
)
from operaciones.models import CentroAyuda, Refugio


class CentroAyudaForm(forms.ModelForm):
    latitud = forms.FloatField(
        min_value=0.6, max_value=12.3, label="Latitud",
        widget=forms.NumberInput(attrs={"step": "0.000001", "placeholder": "10.480600"}),
    )
    longitud = forms.FloatField(
        min_value=-73.4, max_value=-59.8, label="Longitud",
        widget=forms.NumberInput(attrs={"step": "0.000001", "placeholder": "-66.903600"}),
    )

    class Meta:
        model = CentroAyuda
        fields = [
            "nombre", "tipo", "estado", "municipio", "parroquia",
            "direccion", "telefono", "capacidad", "activo", "observaciones",
        ]
        widgets = {
            "direccion": forms.TextInput(attrs={"placeholder": "Av. Principal, sector..."}),
            "telefono": forms.TextInput(attrs={"placeholder": "+584121234567"}),
            "observaciones": forms.Textarea(attrs={"rows": 3}),
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
        widget=forms.NumberInput(attrs={"step": "0.000001"}),
    )
    longitud = forms.FloatField(
        min_value=-73.4, max_value=-59.8, label="Longitud",
        widget=forms.NumberInput(attrs={"step": "0.000001"}),
    )

    class Meta:
        model = Refugio
        fields = [
            "nombre", "estado", "municipio", "parroquia",
            "direccion", "telefono", "capacidad", "ocupacion",
            "estado_operativo", "activo", "observaciones",
        ]

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
