"""Forms de Necesidad con validación de fechas — Fase G."""
from datetime import timedelta

from django import forms
from django.utils import timezone

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
        self.fields["fecha_requerida"].input_formats = ["%Y-%m-%dT%H:%M"]
        # Bloquea en HTML la selección de fechas pasadas (defensa en UI)
        ahora_local = timezone.localtime()
        min_iso = ahora_local.strftime("%Y-%m-%dT%H:%M")
        self.fields["fecha_requerida"].widget.attrs["min"] = min_iso

    # ------------------------------------------------------------------
    # Validaciones explícitas por campo (más confiables que depender del
    # modelo, porque aquí el error siempre llega al usuario)
    # ------------------------------------------------------------------

    def clean_fecha_requerida(self):
        valor = self.cleaned_data.get("fecha_requerida")
        if valor is None:
            return None

        # Comparación con margen de 5 minutos (latencia del cliente)
        ahora = timezone.now()
        margen = timedelta(minutes=5)

        if valor < ahora - margen:
            raise forms.ValidationError(
                "La fecha y hora requerida debe ser desde el momento actual "
                "en adelante. No se pueden registrar necesidades retroactivas."
            )

        # No permitir fechas absurdamente lejanas (> 5 años)
        if valor > ahora + timedelta(days=365 * 5):
            raise forms.ValidationError(
                "La fecha requerida no puede estar a más de 5 años en el futuro."
            )

        return valor

    def clean(self):
        cleaned = super().clean()
        # Re-ejecutamos la validación cruzada del modelo (cantidades, estados)
        # pasando solo los campos que el modelo necesita.
        try:
            instancia = Necesidad(
                refugio=cleaned.get("refugio"),
                recurso=cleaned.get("recurso"),
                cantidad_requerida=cleaned.get("cantidad_requerida"),
                cantidad_recibida=cleaned.get("cantidad_recibida"),
                estado=cleaned.get("estado"),
                prioridad=cleaned.get("prioridad"),
                fecha_requerida=cleaned.get("fecha_requerida"),
            )
            # Solo invocamos las validaciones que NO sean de fecha, porque
            # la fecha ya se validó arriba en clean_fecha_requerida.
            self._validar_cantidades_y_estado(instancia)
        except forms.ValidationError as e:
            if hasattr(e, "error_dict"):
                for field, msgs in e.error_dict.items():
                    for m in msgs:
                        self.add_error(field, m)
            else:
                raise

        return cleaned

    def _validar_cantidades_y_estado(self, instancia):
        """Valida cantidad_recibida ≤ requerida y coherencia de estado."""
        req = instancia.cantidad_requerida
        rec = instancia.cantidad_recibida

        if req is not None and req <= 0:
            raise forms.ValidationError(
                {"cantidad_requerida": msg.NECESIDAD_CANTIDAD_INVALIDA}
            )

        if req is not None and rec is not None and rec > req:
            raise forms.ValidationError(
                {"cantidad_recibida": msg.NECESIDAD_RECIBIDA_EXCEDE}
            )

        if req and rec is not None and instancia.estado != Necesidad.Estados.CANCELADA:
            incoherente = False
            if rec == 0 and instancia.estado != Necesidad.Estados.PENDIENTE:
                incoherente = True
            elif 0 < rec < req and instancia.estado != Necesidad.Estados.PARCIAL:
                incoherente = True
            elif rec >= req and instancia.estado != Necesidad.Estados.CUBIERTA:
                incoherente = True

            if incoherente:
                raise forms.ValidationError(
                    {"estado": msg.NECESIDAD_ESTADO_INCOHERENTE}
                )
