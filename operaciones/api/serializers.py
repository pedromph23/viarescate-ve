from rest_framework import serializers

from operaciones.models import (
    AuditLog,
    CentroAyuda,
    Inventario,
    Mision,
    MovimientoInventario,
    Recurso,
    Refugio,
    ReporteVial,
    Vehiculo,
    Via,
)


class FullCleanModelSerializer(serializers.ModelSerializer):
    """
    Ejecuta las validaciones completas del modelo antes de persistir.
    """

    def create(self, validated_data):
        instance = self.Meta.model(**validated_data)
        instance.full_clean()
        instance.save()
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.full_clean()
        instance.save()
        return instance


class CentroAyudaSerializer(FullCleanModelSerializer):
    class Meta:
        model = CentroAyuda
        fields = "__all__"
        read_only_fields = (
            "id",
            "creado_en",
            "actualizado_en",
        )


class RefugioSerializer(FullCleanModelSerializer):
    porcentaje_ocupacion = serializers.SerializerMethodField()

    class Meta:
        model = Refugio
        fields = "__all__"
        read_only_fields = (
            "id",
            "creado_en",
            "actualizado_en",
            "porcentaje_ocupacion",
        )

    def get_porcentaje_ocupacion(self, obj):
        if obj.capacidad == 0:
            return 0

        return round((obj.ocupacion / obj.capacidad) * 100, 2)


class ViaSerializer(FullCleanModelSerializer):
    class Meta:
        model = Via
        fields = "__all__"
        read_only_fields = (
            "id",
            "creado_en",
            "actualizado_en",
        )


class ReporteVialSerializer(FullCleanModelSerializer):
    class Meta:
        model = ReporteVial
        fields = "__all__"
        read_only_fields = (
            "id",
            "reportado_por",
            "reportado_en",
            "actualizado_en",
            "resuelto_en",
        )


class VehiculoSerializer(FullCleanModelSerializer):
    class Meta:
        model = Vehiculo
        fields = (
            "id",
            "placa",
            "tipo",
            "estado_operativo",
            "capacidad_kg",
            "centro",
            "conductor",
            "ubicacion",
            "activo",
            "observaciones",
            "creado_en",
            "actualizado_en",
        )
        read_only_fields = (
            "id",
            "creado_en",
            "actualizado_en",
        )


class MisionSerializer(FullCleanModelSerializer):
    def validate(self, attrs):
        if self.instance is not None and "estado_mision" in attrs:
            raise serializers.ValidationError(
                {
                    "estado_mision": (
                        "El estado de la misión no puede modificarse "
                        "directamente. Debe utilizarse una transición "
                        "controlada de misión."
                    )
                }
            )

        return attrs

    class Meta:
        model = Mision
        fields = (
            "id",
            "codigo",
            "nombre",
            "descripcion",
            "estado_mision",
            "modo_ruta",
            "origen",
            "destino",
            "vehiculo",
            "coordinador",
            "prioridad",
            "distancia_km",
            "tiempo_estimado_minutos",
            "ruta",
            "planificada_en",
            "iniciada_en",
            "entregada_en",
            "cancelada_en",
            "observaciones",
        )
        read_only_fields = (
            "id",
            "codigo",
            "planificada_en",
            "iniciada_en",
            "entregada_en",
            "cancelada_en",
        )

    def create(self, validated_data):
        from operaciones.services import MissionService

        instance = Mision(**validated_data)
        MissionService.prepare_for_create(instance)
        instance.save()
        return instance


class RecursoSerializer(FullCleanModelSerializer):
    class Meta:
        model = Recurso
        fields = "__all__"
        read_only_fields = ("id",)


class InventarioSerializer(FullCleanModelSerializer):
    def validate(self, attrs):
        if self.instance is not None and "cantidad" in attrs:
            raise serializers.ValidationError(
                {
                    "cantidad": (
                        "La cantidad no puede modificarse directamente. "
                        "Debe utilizarse un movimiento de inventario."
                    )
                }
            )

        return attrs

    class Meta:
        model = Inventario
        fields = (
            "id",
            "centro",
            "recurso",
            "cantidad",
            "minimo",
            "actualizado_en",
        )
        read_only_fields = (
            "id",
            "actualizado_en",
        )


class MovimientoInventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimientoInventario
        fields = (
            "id",
            "inventario",
            "tipo",
            "cantidad",
            "referencia",
            "observaciones",
            "realizado_por",
            "creado_en",
        )
        read_only_fields = (
            "id",
            "realizado_por",
            "creado_en",
        )

    def validate_cantidad(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "La cantidad no puede ser negativa."
            )

        return value


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = (
            "id",
            "usuario",
            "accion",
            "modulo",
            "objeto_tipo",
            "objeto_id",
            "fecha",
            "ip",
            "detalles",
            "resultado",
        )
        read_only_fields = (
            "id",
            "usuario",
            "accion",
            "modulo",
            "objeto_tipo",
            "objeto_id",
            "fecha",
            "ip",
            "detalles",
            "resultado",
        )
