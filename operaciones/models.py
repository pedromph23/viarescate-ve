import uuid

from django.conf import settings
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone



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

    fecha_ultimo_censo = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha y hora del último censo de personas.",
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
        from core import messages as msg
        from core.validators import validar_fecha_futura

        errors = {}

        if self.ocupacion > self.capacidad:
            errors["ocupacion"] = (
                "La ocupación no puede superar la capacidad del refugio."
            )

        try:
            validar_fecha_futura(self.fecha_ultimo_censo, msg.FECHA_CENSO_FUTURA)
        except ValidationError as e:
            errors["fecha_ultimo_censo"] = e.messages

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

    # --- Campos ampliados para reportes completos ---
    fecha_incidente = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Cuándo ocurrió el incidente (puede ser distinto de la fecha de reporte).",
    )

    foto = models.ImageField(
        upload_to="reportes/%Y/%m/",
        null=True,
        blank=True,
        help_text="Fotografía principal del incidente (JPG, PNG o WEBP — máx 5 MB).",
    )

    afecta_transito = models.BooleanField(
        default=True,
        help_text="¿El incidente está bloqueando o afectando el tránsito?",
    )

    # --- Metadatos temporales ---
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

    def clean(self):
        super().clean()
        from core import messages as msg
        from core.validators import (
            validar_fecha_con_referencia,
            validar_fecha_en_pasado_o_ahora,
            validar_orden_fechas,
        )

        errors = {}

        # Fecha de referencia: reportado_en (server-set) o now() para nuevas instancias
        referencia = self.reportado_en or timezone.now()

        # fecha_incidente: solo HOY (desde 00:00 local).
        # Los reportes ciudadanos son sobre el presente.
        if self.fecha_incidente is not None:
            try:
                validar_fecha_con_referencia(
                    self.fecha_incidente,
                    referencia=referencia,
                    grace_minutos=5,
                    solo_hoy=True,
                    contexto="incidente",
                )
            except ValidationError as e:
                errors["fecha_incidente"] = e.messages

        # resuelto_en: no puede ser futuro Y debe ser >= reportado_en
        if self.resuelto_en is not None:
            try:
                validar_fecha_en_pasado_o_ahora(
                    self.resuelto_en,
                    grace_minutos=5,
                    contexto="resolución",
                )
            except ValidationError as e:
                errors["resuelto_en"] = e.messages

            if self.reportado_en:
                try:
                    validar_orden_fechas(
                        self.reportado_en,
                        self.resuelto_en,
                        msg.FECHA_RESOLUCION_ANTES_REPORTE,
                    )
                except ValidationError as e:
                    errors["resuelto_en"] = e.messages

        if errors:
            raise ValidationError(errors)

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

    fecha_salida_planificada = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha y hora prevista de salida del centro de acopio.",
    )
    fecha_entrega_estimada = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha y hora prevista de entrega en el refugio.",
    )

    planificada_en = models.DateTimeField(auto_now_add=True)
    iniciada_en = models.DateTimeField(null=True, blank=True)
    entregada_en = models.DateTimeField(null=True, blank=True)
    cancelada_en = models.DateTimeField(null=True, blank=True)

    observaciones = models.TextField(blank=True)

    def clean(self):
        super().clean()
        from core import messages as msg
        from core.validators import validar_orden_fechas

        errors = {}

        # fecha_entrega_estimada >= fecha_salida_planificada
        try:
            validar_orden_fechas(
                self.fecha_salida_planificada,
                self.fecha_entrega_estimada,
                msg.FECHA_ENTREGA_ANTES_SALIDA,
            )
        except ValidationError as e:
            errors["fecha_entrega_estimada"] = e.messages

        # entregada_en (real) >= fecha_salida_planificada
        try:
            validar_orden_fechas(
                self.fecha_salida_planificada,
                self.entregada_en,
                msg.FECHA_ENTREGA_REAL_ANTES_SALIDA,
            )
        except ValidationError as e:
            errors["entregada_en"] = e.messages

        # entregada_en >= iniciada_en
        try:
            validar_orden_fechas(
                self.iniciada_en,
                self.entregada_en,
                "La fecha de entrega real no puede ser anterior a la fecha de inicio.",
            )
        except ValidationError as e:
            errors["entregada_en"] = e.messages

        # NUEVO: fechas REALES no pueden estar en el futuro
        from core.validators import validar_fecha_en_pasado_o_ahora

        for campo, contexto in [
            ("iniciada_en", "inicio de la misión"),
            ("entregada_en", "entrega real"),
            ("cancelada_en", "cancelación"),
        ]:
            fecha = getattr(self, campo, None)
            if fecha is not None:
                try:
                    validar_fecha_en_pasado_o_ahora(
                        fecha, grace_minutos=5, contexto=contexto,
                    )
                except ValidationError as e:
                    errors[campo] = e.messages

        if errors:
            raise ValidationError(errors)

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


class Necesidad(models.Model):
    """
    Necesidad humanitaria: qué recurso falta en un refugio, cuánto y con
    qué prioridad. Permite priorizar la distribución desde centros de acopio.
    """

    class Prioridades(models.TextChoices):
        BAJA = "BAJA", "Baja"
        MEDIA = "MEDIA", "Media"
        ALTA = "ALTA", "Alta"
        CRITICA = "CRITICA", "Crítica"

    class Estados(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        PARCIAL = "PARCIAL", "Parcialmente cubierta"
        CUBIERTA = "CUBIERTA", "Cubierta"
        CANCELADA = "CANCELADA", "Cancelada"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    refugio = models.ForeignKey(
        Refugio,
        on_delete=models.CASCADE,
        related_name="necesidades",
    )
    recurso = models.ForeignKey(
        Recurso,
        on_delete=models.PROTECT,
        related_name="necesidades",
    )

    cantidad_requerida = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )
    cantidad_recibida = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    prioridad = models.CharField(
        max_length=10,
        choices=Prioridades.choices,
        default=Prioridades.MEDIA,
        db_index=True,
    )
    estado = models.CharField(
        max_length=10,
        choices=Estados.choices,
        default=Estados.PENDIENTE,
        db_index=True,
    )

    fecha_requerida = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha y hora en que se requiere la ayuda.",
    )
    observaciones = models.TextField(blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-prioridad", "fecha_requerida")
        constraints = [
            models.UniqueConstraint(
                fields=("refugio", "recurso"),
                name="uq_necesidad_refugio_recurso",
            ),
        ]
        indexes = [
            models.Index(fields=("prioridad", "estado")),
            models.Index(fields=("refugio", "estado")),
        ]
        verbose_name = "Necesidad"
        verbose_name_plural = "Necesidades"

    @property
    def cantidad_pendiente(self):
        return self.cantidad_requerida - self.cantidad_recibida

    def clean(self):
        super().clean()
        from core import messages as msg
        from core.validators import validar_fecha_no_pasada

        errors = {}

        # cantidad_requerida > 0
        if self.cantidad_requerida is not None and self.cantidad_requerida <= 0:
            errors["cantidad_requerida"] = msg.NECESIDAD_CANTIDAD_INVALIDA

        # cantidad_recibida <= cantidad_requerida
        if (
            self.cantidad_requerida is not None
            and self.cantidad_recibida is not None
            and self.cantidad_recibida > self.cantidad_requerida
        ):
            errors["cantidad_recibida"] = msg.NECESIDAD_RECIBIDA_EXCEDE

        # fecha_requerida: siempre debe ser >= hoy (con margen de 5 min)
        # No hay excepción ni siquiera para updates: registrar una necesidad
        # en el pasado no tiene sentido operativo.
        if self.fecha_requerida is not None:
            from datetime import timedelta
            from django.utils import timezone as tz
            ahora = tz.now()
            if self.fecha_requerida < ahora - timedelta(minutes=5):
                errors["fecha_requerida"] = msg.NECESIDAD_FECHA_PASADA
            elif self.fecha_requerida > ahora + timedelta(days=365 * 5):
                errors["fecha_requerida"] = (
                    "La fecha requerida no puede estar a más de 5 años en el futuro."
                )

        # Coherencia estado <-> cantidades
        if self.cantidad_requerida and self.cantidad_recibida is not None:
            if self.estado != self.Estados.CANCELADA:
                if self.cantidad_recibida == 0 and self.estado != self.Estados.PENDIENTE:
                    errors["estado"] = msg.NECESIDAD_ESTADO_INCOHERENTE
                elif (
                    0 < self.cantidad_recibida < self.cantidad_requerida
                    and self.estado != self.Estados.PARCIAL
                ):
                    errors["estado"] = msg.NECESIDAD_ESTADO_INCOHERENTE
                elif (
                    self.cantidad_recibida >= self.cantidad_requerida
                    and self.estado != self.Estados.CUBIERTA
                ):
                    errors["estado"] = msg.NECESIDAD_ESTADO_INCOHERENTE

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.refugio} necesita {self.cantidad_pendiente} {self.recurso.unidad} de {self.recurso.nombre}"


class FotoReporte(models.Model):
    """Fotos adicionales asociadas a un reporte vial."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporte = models.ForeignKey(
        ReporteVial,
        on_delete=models.CASCADE,
        related_name="fotos_adicionales",
    )
    imagen = models.ImageField(upload_to="reportes/galeria/%Y/%m/")
    descripcion = models.CharField(max_length=200, blank=True)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("creada_en",)
        verbose_name = "Foto de reporte"
        verbose_name_plural = "Fotos de reporte"

    def __str__(self):
        return f"Foto de {self.reporte.titulo[:40]}"


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


# ---------------------------------------------------------------------------
# Modelos de predicción / IA (importados al final para que Django los registre)
# ---------------------------------------------------------------------------
from .prediccion_models import (  # noqa: E402,F401
    AlertaPredictiva,
    PrediccionDemanda,
    PrediccionMision,
)
