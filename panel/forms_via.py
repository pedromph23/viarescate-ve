"""Formulario de Vías con editor de línea en mapa."""
from django import forms
from django.contrib.gis.geos import LineString

from core import messages as msg
from core.validators import (
    validar_codigo_interno,
    validar_nombre_propio,
)
from operaciones.models import Via


class ViaForm(forms.ModelForm):
    """Formulario de vía con editor de LineString desde el mapa."""

    # JSON con lista de puntos: [{"lat": ..., "lng": ...}, ...]
    puntos_json = forms.CharField(
        widget=forms.HiddenInput(attrs={"id": "id_puntos_json"}),
        required=False,
        help_text="Puntos del trazado en formato JSON.",
    )

    class Meta:
        model = Via
        fields = [
            "nombre",
            "codigo",
            "estado",
            "estado_vial",
            "velocidad_referencial",
            "activa",
            "observaciones",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={
                "placeholder": "Ej: Autopista Francisco Fajardo",
                "data-validator": "nombre",
                "minlength": "3",
                "maxlength": "200",
            }),
            "codigo": forms.TextInput(attrs={
                "placeholder": "Ej: VIA_CCS_001",
                "data-validator": "codigo",
                "pattern": "[A-Z][A-Z0-9_]{2,29}",
                "maxlength": "50",
                "style": "text-transform: uppercase;",
            }),
            "estado": forms.Select(attrs={"required": "required"}),
            "estado_vial": forms.Select(attrs={"required": "required"}),
            "velocidad_referencial": forms.NumberInput(attrs={
                "data-validator": "entero_positivo",
                "min": "0",
                "max": "300",
                "inputmode": "numeric",
                "placeholder": "Ej: 60",
            }),
            "activa": forms.CheckboxInput(attrs={"class": "panel-toggle"}),
            "observaciones": forms.Textarea(attrs={
                "rows": 3,
                "maxlength": "1000",
                "placeholder": "Notas adicionales (opcional)",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["codigo"].required = False

        # Si editamos, cargar los puntos del LineString actual
        if self.instance and self.instance.pk and self.instance.geometria:
            coords = self.instance.geometria.coords  # ((lng, lat), (lng, lat), ...)
            puntos = [{"lat": c[1], "lng": c[0]} for c in coords]
            import json
            self.fields["puntos_json"].initial = json.dumps(puntos)

    def clean_nombre(self):
        return validar_nombre_propio(self.cleaned_data["nombre"])

    def clean_codigo(self):
        valor = self.cleaned_data.get("codigo", "").strip()
        if not valor:
            return ""
        return validar_codigo_interno(valor)

    def clean_puntos_json(self):
        import json
        raw = self.cleaned_data.get("puntos_json", "").strip()
        if not raw:
            raise forms.ValidationError(
                "Debes dibujar al menos 2 puntos en el mapa para trazar la vía."
            )
        try:
            puntos = json.loads(raw)
        except Exception:
            raise forms.ValidationError("Formato de puntos inválido.")

        if not isinstance(puntos, list) or len(puntos) < 2:
            raise forms.ValidationError(
                "La vía necesita al menos 2 puntos en el mapa."
            )

        # Validar cada punto dentro de Venezuela
        from core.validators import validar_coordenadas_ve
        for p in puntos:
            if "lat" not in p or "lng" not in p:
                raise forms.ValidationError("Cada punto debe tener lat y lng.")
            validar_coordenadas_ve(p["lat"], p["lng"])

        return puntos

    def save(self, commit=True):
        instance = super().save(commit=False)
        puntos = self.cleaned_data["puntos_json"]

        # Construir LineString: (lng, lat) — PostGIS usa lng primero
        coords = [(p["lng"], p["lat"]) for p in puntos]
        instance.geometria = LineString(coords, srid=4326)

        if commit:
            instance.save()
        return instance
