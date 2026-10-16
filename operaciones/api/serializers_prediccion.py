from rest_framework import serializers

from operaciones.models import (
    AlertaPredictiva,
    PrediccionDemanda,
    PrediccionMision,
)


class PrediccionDemandaSerializer(serializers.ModelSerializer):
    refugio_nombre = serializers.CharField(source="refugio.nombre", read_only=True)
    recurso_nombre = serializers.CharField(source="recurso.nombre", read_only=True)
    recurso_unidad = serializers.CharField(source="recurso.unidad", read_only=True)

    class Meta:
        model = PrediccionDemanda
        fields = (
            "id", "refugio", "refugio_nombre",
            "recurso", "recurso_nombre", "recurso_unidad",
            "horizonte", "cantidad_predicha", "confianza",
            "modelo_usado", "generado_en",
        )


class PrediccionMisionSerializer(serializers.ModelSerializer):
    mision_codigo = serializers.CharField(source="mision.codigo", read_only=True)
    mision_nombre = serializers.CharField(source="mision.nombre", read_only=True)

    class Meta:
        model = PrediccionMision
        fields = (
            "id", "mision", "mision_codigo", "mision_nombre",
            "retraso_estimado_minutos", "probabilidad_retraso",
            "nivel_riesgo", "razones", "generado_en",
        )


class AlertaPredictivaSerializer(serializers.ModelSerializer):
    refugio_nombre = serializers.CharField(source="refugio.nombre", read_only=True)
    recurso_nombre = serializers.CharField(source="recurso.nombre", read_only=True)
    mision_codigo = serializers.CharField(source="mision.codigo", read_only=True)

    class Meta:
        model = AlertaPredictiva
        fields = (
            "id", "tipo", "severidad", "titulo", "descripcion",
            "accion_recomendada", "refugio", "refugio_nombre",
            "recurso", "recurso_nombre", "mision", "mision_codigo",
            "datos_soporte", "activa", "reconocida", "creada_en",
        )
