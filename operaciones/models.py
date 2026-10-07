import uuid

from django.conf import settings
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator



class IntegridadTerritorialMixin:
    def clean(self):
        super().clean()
        errors = {}

        if self.estado_id and self.municipio_id:
            if self.municipio.estado_id != self.estado_id:
                errors["municipio"] = (
                    "El municipio seleccionado no pertenece al estado indicado."
                )

        if self.municipio_id and self.parroquia_id:
            if self.parroquia.municipio_id != self.municipio_id:
                errors["parroquia"] = (
                    "La parroquia seleccionada no pertenece al municipio indicado."
                )

        if errors:
            raise ValidationError(errors)


class CentroAyuda(IntegridadTerritorialMixin, models.Model):
    class Tipos(models.TextChoices):
        LOGISTICO = "LOGISTICO", "Logístico"
        DISTRIBUCION = "DISTRIBUCION", "Distribución"
        COORDINACION = "COORDINACION", "Coordinación"
        MIXTO = "MIXTO", "Mixto"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=180)
    tipo = models.CharField(
        max_length=20,
        choices=Tipos.choices,
        default=Tipos.MIXTO,
        db_index=True,
    )

    estado = models.ForeignKey(
        "core.Estado",
        on_delete=models.PROTECT,
        related_name="centros_ayuda",
    )
    municipio = models.ForeignKey(
        "core.Municipio",
        on_delete=models.PROTECT,
        related_name="centros_ayuda",
    )
    parroquia = models.ForeignKey(
        "core.Parroquia",
        on_delete=models.PROTECT,
        related_name="centros_ayuda",
    )

    ubicacion = models.PointField(srid=4326)
    direccion = models.TextField(blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    capacidad = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True, db_index=True)
    observaciones = models.TextField(blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("nombre",)
        indexes = [
            models.Index(fields=("tipo", "activo")),
        ]
        verbose_name = "Centro de ayuda"
        verbose_name_plural = "Centros de ayuda"

    def __str__(self):
        return self.nombre


class Refugio(IntegridadTerritorialMixin, models.Model):
    class Estados(models.TextChoices):
        DISPONIBLE = "DISPONIBLE", "Disponible"
        COMPLETO = "COMPLETO", "Completo"
        INACTIVO = "INACTIVO", "Inactivo"
        MANTENIMIENTO = "MANTENIMIENTO", "Mantenimiento"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=180)

    estado = models.ForeignKey(
        "core.Estado",
        on_delete=models.PROTECT,
        related_name="refugios",
    )
    municipio = models.ForeignKey(
        "core.Municipio",
        on_delete=models.PROTECT,
        related_name="refugios",
    )
    parroquia = models.ForeignKey(
        "core.Parroquia",
        on_delete=models.PROTECT,
        related_name="refugios",
    )

    ubicacion = models.PointField(srid=4326)
    direccion = models.TextField(blank=True)
    telefono = models.CharField(max_length=30, blank=True)

    capacidad = models.PositiveIntegerField(default=0)
    ocupacion = models.PositiveIntegerField(default=0)
    estado_operativo = models.CharField(
        max_length=20,
        choices=Estados.choices,
        default=Estados.DISPONIBLE,
        db_index=True,
    )

    activo = models.BooleanField(default=True, db_index=True)
    observaciones = models.TextField(blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("nombre",)
        constraints = [
            models.CheckConstraint(
                condition=models.Q(ocupacion__gte=0) & models.Q(ocupacion__lte=models.F("capacidad")),
                name="ck_refugio_ocupacion_valida",
            ),
        ]
        indexes = [
            models.Index(fields=("estado_operativo", "activo")),
        ]
        verbose_name = "Refugio"
        verbose_name_plural = "Refugios"

    def clean(self):
        super().clean()
        errors = {}

        if self.ocupacion > self.capacidad:
            errors["ocupacion"] = (
                "La ocupación no puede superar la capacidad del refugio."
            )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return self.nombre


class Via(models.Model):
    class Estados(models.TextChoices):
        NORMAL = "NORMAL", "Normal"
        PRECAUCION = "PRECAUCION", "Precaución"
        AFECTADA = "AFECTADA", "Afectada"
        CRITICA = "CRITICA", "Crítica"
        CERRADA = "CERRADA", "Cerrada"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=200)
    codigo = models.CharField(max_length=50, blank=True)

    estado = models.ForeignKey(
        "core.Estado",
        on_delete=models.PROTECT,
        related_name="vias",
    )

    geometria = models.LineStringField(srid=4326)
    estado_vial = models.CharField(
        max_length=20,
        choices=Estados.choices,
        default=Estados.NORMAL,
        db_index=True,
    )

    velocidad_referencial = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Velocidad referencial en km/h.",
    )
    activa = models.BooleanField(default=True, db_index=True)
    observaciones = models.TextField(blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("nombre",)
        indexes = [
            models.Index(fields=("estado_vial", "activa")),
        ]
        verbose_name = "Vía"
        verbose_name_plural = "Vías"

    def __str__(self):
        return self.nombre


class ReporteVial(models.Model):
    class Tipos(models.TextChoices):
        ACCIDENTE = "ACCIDENTE", "Accidente"
        INUNDACION = "INUNDACION", "Inundación"
        DERRUMBE = "DERRUMBE", "Derrumbe"
        CIERRE = "CIERRE", "Cierre"
        PUENTE_DANADO = "PUENTE_DANADO", "Puente dañado"
        OBSTACULO = "OBSTACULO", "Obstáculo"
        PROTESTA = "PROTESTA", "Protesta"
        TRAFICO = "TRAFICO", "Tráfico"
        OBRAS = "OBRAS", "Obras"
        OTRO = "OTRO", "Otro"

    class Estados(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        CONFIRMADO = "CONFIRMADO", "Confirmado"
        RECHAZADO = "RECHAZADO", "Rechazado"
        RESUELTO = "RESUELTO", "Resuelto"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo = models.CharField(
        max_length=20,
        choices=Tipos.choices,
        db_index=True,
    )
    estado_reporte = models.CharField(
        max_length=20,
        choices=Estados.choices,
        default=Estados.PENDIENTE,
        db_index=True,
    )

    via = models.ForeignKey(
        Via,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reportes",
    )

    ubicacion = models.PointField(srid=4326)
    titulo = models.CharField(max_length=180)
    descripcion = models.TextField()

    severidad = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Nivel de severidad de 1 a 5.",
    )

    reportado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reportes_viales",
    )

    reportado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    resuelto_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-reportado_en",)
        constraints = [
            models.CheckConstraint(
                condition=models.Q(severidad__gte=1) & models.Q(severidad__lte=5),
                name="ck_reporte_vial_severidad_valida",
            ),
        ]
        indexes = [
            models.Index(fields=("tipo", "estado_reporte")),
            models.Index(fields=("reportado_en",)),
        ]
        verbose_name = "Reporte vial"
        verbose_name_plural = "Reportes viales"

    def __str__(self):
        return self.titulo


class Vehiculo(models.Model):
    class Tipos(models.TextChoices):
        CAMION = "CAMION", "Camión"
        CAMIONETA = "CAMIONETA", "Camioneta"
        AMBULANCIA = "AMBULANCIA", "Ambulancia"
        AUTOBUS = "AUTOBUS", "Autobús"
        OTRO = "OTRO", "Otro"

    class Estados(models.TextChoices):
        DISPONIBLE = "DISPONIBLE", "Disponible"
        EN_RUTA = "EN_RUTA", "En ruta"
        MANTENIMIENTO = "MANTENIMIENTO", "Mantenimiento"
        INACTIVO = "INACTIVO", "Inactivo"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    placa = models.CharField(max_length=20, unique=True)
    tipo = models.CharField(max_length=20, choices=Tipos.choices)
    estado_operativo = models.CharField(
        max_length=20,
        choices=Estados.choices,
        default=Estados.DISPONIBLE,
        db_index=True,
    )

    capacidad_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    centro = models.ForeignKey(
        CentroAyuda,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vehiculos",
    )

    conductor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vehiculos_conducidos",
    )

    ubicacion = models.PointField(srid=4326, null=True, blank=True)
    activo = models.BooleanField(default=True, db_index=True)
    observaciones = models.TextField(blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("placa",)
        indexes = [
            models.Index(fields=("estado_operativo", "activo")),
        ]
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"

    def __str__(self):
        return self.placa


class Mision(models.Model):
    class Estados(models.TextChoices):
        PLANIFICADA = "PLANIFICADA", "Planificada"
        ASIGNADA = "ASIGNADA", "Asignada"
        EN_RUTA = "EN_RUTA", "En ruta"
        ENTREGADA = "ENTREGADA", "Entregada"
        CANCELADA = "CANCELADA", "Cancelada"

    class ModosRuta(models.TextChoices):
        MAS_CORTA = "MAS_CORTA", "Más corta"
        MAS_RAPIDA = "MAS_RAPIDA", "Más rápida"
        MAS_SEGURA = "MAS_SEGURA", "Más segura"
        HUMANITARIA = "HUMANITARIA", "Humanitaria"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=40, unique=True)

    nombre = models.CharField(max_length=180)
    descripcion = models.TextField(blank=True)

    estado_mision = models.CharField(
        max_length=20,
        choices=Estados.choices,
        default=Estados.PLANIFICADA,
        db_index=True,
    )
    modo_ruta = models.CharField(
        max_length=20,
        choices=ModosRuta.choices,
        default=ModosRuta.HUMANITARIA,
        db_index=True,
    )

    origen = models.PointField(srid=4326)
    destino = models.PointField(srid=4326)

    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="misiones",
    )

    coordinador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="misiones_coordinadas",
    )

    prioridad = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Prioridad de 1 a 5.",
    )

    distancia_km = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )

    tiempo_estimado_minutos = models.PositiveIntegerField(null=True, blank=True)

    ruta = models.LineStringField(srid=4326, null=True, blank=True)

    planificada_en = models.DateTimeField(auto_now_add=True)
    iniciada_en = models.DateTimeField(null=True, blank=True)
    entregada_en = models.DateTimeField(null=True, blank=True)
    cancelada_en = models.DateTimeField(null=True, blank=True)

    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ("-planificada_en",)
        constraints = [
            models.CheckConstraint(
                condition=models.Q(prioridad__gte=1) & models.Q(prioridad__lte=5),
                name="ck_mision_prioridad_valida",
            ),
        ]
        indexes = [
            models.Index(fields=("estado_mision", "modo_ruta")),
            models.Index(fields=("prioridad", "estado_mision")),
        ]
        verbose_name = "Misión"
        verbose_name_plural = "Misiones"

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Recurso(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=150, unique=True)
    unidad = models.CharField(max_length=30)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ("nombre",)
        verbose_name = "Recurso"
        verbose_name_plural = "Recursos"

    def __str__(self):
        return self.nombre


class Inventario(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    centro = models.ForeignKey(
        CentroAyuda,
        on_delete=models.CASCADE,
        related_name="inventarios",
    )
    recurso = models.ForeignKey(
        Recurso,
        on_delete=models.PROTECT,
        related_name="inventarios",
    )

    cantidad = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    minimo = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("centro__nombre", "recurso__nombre")
        constraints = [
            models.UniqueConstraint(
                fields=("centro", "recurso"),
                name="uq_inventario_centro_recurso",
            ),
        ]
        indexes = [
            models.Index(fields=("centro", "recurso")),
        ]
        verbose_name = "Inventario"
        verbose_name_plural = "Inventarios"

    def __str__(self):
        return f"{self.centro} - {self.recurso}"


class MovimientoInventario(models.Model):
    class Tipos(models.TextChoices):
        ENTRADA = "ENTRADA", "Entrada"
        SALIDA = "SALIDA", "Salida"
        AJUSTE = "AJUSTE", "Ajuste"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    inventario = models.ForeignKey(
        Inventario,
        on_delete=models.PROTECT,
        related_name="movimientos",
    )
    tipo = models.CharField(max_length=10, choices=Tipos.choices, db_index=True)
    cantidad = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    referencia = models.CharField(max_length=120, blank=True)
    observaciones = models.TextField(blank=True)

    realizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimientos_inventario",
    )

    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-creado_en",)
        indexes = [
            models.Index(fields=("tipo", "creado_en")),
        ]
        verbose_name = "Movimiento de inventario"
        verbose_name_plural = "Movimientos de inventario"

    def __str__(self):
        return f"{self.tipo} - {self.cantidad}"


class AuditLog(models.Model):
    class Resultados(models.TextChoices):
        EXITO = "EXITO", "Éxito"
        ERROR = "ERROR", "Error"
        RECHAZADO = "RECHAZADO", "Rechazado"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="registros_auditoria",
    )

    accion = models.CharField(max_length=100, db_index=True)
    modulo = models.CharField(max_length=100, db_index=True)
    objeto_tipo = models.CharField(max_length=100, blank=True)
    objeto_id = models.CharField(max_length=100, blank=True)

    fecha = models.DateTimeField(auto_now_add=True, db_index=True)
    ip = models.GenericIPAddressField(null=True, blank=True)

    detalles = models.JSONField(default=dict, blank=True)
    resultado = models.CharField(
        max_length=12,
        choices=Resultados.choices,
        default=Resultados.EXITO,
        db_index=True,
    )

    class Meta:
        ordering = ("-fecha",)
        indexes = [
            models.Index(fields=("modulo", "accion", "fecha")),
            models.Index(fields=("usuario", "fecha")),
        ]
        verbose_name = "Registro de auditoría"
        verbose_name_plural = "Registros de auditoría"

    def __str__(self):
        return f"{self.accion} - {self.modulo}"
