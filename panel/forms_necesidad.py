"""Forms de Necesidad con validación de fechas — Fase G."""
from django import forms

from core import messages as msg
from operaciones.models import Necesidad


class NecesidadForm(forms.ModelForm):
    """Formulario para registrar/editar necesidades de un refugio."""

    class Meta:
        model = Necesidad
        fields = [
            "refugio",
            "recurso",
            "cantidad_requerida",
            "cantidad_recibida",
            "prioridad",
            "estado",
            "fecha_requerida",
            "observaciones",
        ]
        widgets = {
            "fecha_requerida": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "observaciones": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # El widget datetime-local necesita este formato de entrada
        self.fields["fecha_requerida"].input_formats = ["%Y-%m-%dT%H:%M"]

    def clean(self):
        cleaned = super().clean()
        # La validación cruzada vive en Necesidad.clean()
        # Aquí solo propagamos errores de modelo a los campos del form
        try:
            instancia = Necesidad(**{k: v for k, v in cleaned.items() if k in self.fields})
            instancia.clean()
        except forms.ValidationError as e:
            for field, msgs in e.error_dict.items():
                for m in msgs:
                    self.add_error(field, m)
        return cleaned
