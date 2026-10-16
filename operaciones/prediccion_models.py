"""
Modelos para almacenar predicciones generadas por el pipeline de IA.
Las predicciones se calculan offline y se sirven como datos pre-computados.
"""
import uuid

from django.db import models


class PrediccionDemanda(models.Model):
    """Predicción de demanda futura de un recurso en un refugio."""

    class Horizontes(models.TextChoices):
        DIAS_7 = "DIAS_7", "Próximos 7 días"
        DIAS_14 = "DIAS_14", "Próximos 14 días"
        DIAS_30 = "DIAS_30", "Próximos 30 días"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    refugio = models.ForeignKey(
        "operaciones.Refugio",
        on_delete=models.CASCADE,
        related_name="predicciones_demanda",
    )
    recurso = models.ForeignKey(
        "operaciones.Recurso",
        on_delete=models.CASCADE,
        related_name="predicciones_demanda",
    )

    horizonte = models.CharField(max_length=10, choices=Horizontes.choices, db_index=True)

    cantidad_predicha = models.DecimalField(max_digits=14, decimal_places=2)
    confianza = models.DecimalField(
        max_digits=5, decimal_places=2,
        help_text="Nivel de confianza del modelo (0-100)."
    )
    modelo_usado = models.CharField(max_length=50, default="prophet")

    generado_en = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-generado_en",)
        constraints = [
            models.UniqueConstraint(
                fields=("refugio", "recurso", "horizonte"),
                name="uq_prediccion_refugio_recurso_horizonte",
            ),
        ]
        indexes = [
            models.Index(fields=("generado_en", "horizonte")),
        ]
        verbose_name = "Predicción de demanda"
        verbose_name_plural = "Predicciones de demanda"

    def __str__(self):
        return f"{self.refugio} · {self.recurso} · {self.horizonte}"


class PrediccionMision(models.Model):
    """Predicción de retraso o riesgo para una misión."""

    class NivelesRiesgo(models.TextChoices):
        BAJO = "BAJO", "Bajo"
        MEDIO = "MEDIO", "Medio"
        ALTO = "ALTO", "Alto"
        CRITICO = "CRITICO", "Crítico"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    mision = models.OneToOneField(
        "operaciones.Mision",
        on_delete=models.CASCADE,
        related_name="prediccion",
    )

    retraso_estimado_minutos = models.IntegerField(
        null=True, blank=True,
        help_text="Retraso estimado en minutos respecto a la fecha estimada."
    )
    probabilidad_retraso = models.DecimalField(
        max_digits=5, decimal_places=2,
        help_text="Probabilidad de retraso (0-100)."
    )
    nivel_riesgo = models.CharField(
        max_length=10, choices=NivelesRiesgo.choices, db_index=True,
    )

    razones = models.JSONField(
        default=list, blank=True,
        help_text="Lista de factores que explican la predicción."
    )

    generado_en = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-generado_en",)
        verbose_name = "Predicción de misión"
        verbose_name_plural = "Predicciones de misión"

    def __str__(self):
        return f"{self.mision.codigo} · {self.nivel_riesgo}"


class AlertaPredictiva(models.Model):
    """Alerta generada cuando el modelo detecta una situación que requiere acción."""

    class Tipos(models.TextChoices):
        DEMANDA_ALTA = "DEMANDA_ALTA", "Demanda alta proyectada"
        REFUGIO_SATURACION = "REFUGIO_SATURACION", "Refugio en riesgo de saturación"
        MISION_RIESGO = "MISION_RIESGO", "Misión en riesgo de retraso"
        INVENTARIO_INSUFICIENTE = "INVENTARIO_INSUFICIENTE", "Inventario insuficiente proyectado"
        VIA_RIESGO = "VIA_RIESGO", "Vía con riesgo de cierre"

    class Severidades(models.TextChoices):
        INFO = "INFO", "Informativa"
        ADVERTENCIA = "ADVERTENCIA", "Advertencia"
        CRITICA = "CRITICA", "Crítica"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tipo = models.CharField(max_length=30, choices=Tipos.choices, db_index=True)
    severidad = models.CharField(
        max_length=15, choices=Severidades.choices, default=Severidades.INFO,
        db_index=True,
    )

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    accion_recomendada = models.TextField(blank=True)

    refugio = models.ForeignKey(
        "operaciones.Refugio",
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="alertas_predictivas",
    )
    recurso = models.ForeignKey(
        "operaciones.Recurso",
        on_delete=models.CASCADE,
        null=True, blank=True,
    )
    mision = models.ForeignKey(
        "operaciones.Mision",
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="alertas_predictivas",
    )

    datos_soporte = models.JSONField(
        default=dict, blank=True,
        help_text="Datos numéricos que sustentan la alerta."
    )

    activa = models.BooleanField(default=True, db_index=True)
    reconocida = models.BooleanField(default=False, db_index=True)
    reconocida_por = models.ForeignKey(
        "usuarios.Usuario",
        on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    reconocida_en = models.DateTimeField(null=True, blank=True)

    creada_en = models.DateTimeField(auto_now_add=True, db_index=True)
    expira_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-creada_en",)
        indexes = [
            models.Index(fields=("activa", "severidad")),
            models.Index(fields=("tipo", "activa")),
        ]
        verbose_name = "Alerta predictiva"
        verbose_name_plural = "Alertas predictivas"

    def __str__(self):
        return f"[{self.severidad}] {self.titulo}"
