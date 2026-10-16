from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from operaciones.models import (
    AlertaPredictiva,
    PrediccionDemanda,
    PrediccionMision,
)

from .serializers_prediccion import (
    AlertaPredictivaSerializer,
    PrediccionDemandaSerializer,
    PrediccionMisionSerializer,
)


class PrediccionDemandaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PrediccionDemanda.objects.select_related("refugio", "recurso")
    serializer_class = PrediccionDemandaSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["horizonte", "refugio", "recurso"]


class PrediccionMisionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PrediccionMision.objects.select_related("mision")
    serializer_class = PrediccionMisionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["nivel_riesgo"]


class AlertaPredictivaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AlertaPredictiva.objects.select_related("refugio", "recurso", "mision")
    serializer_class = AlertaPredictivaSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["tipo", "severidad", "activa", "reconocida"]

    @action(detail=True, methods=["post"])
    def reconocer(self, request, pk=None):
        alerta = self.get_object()
        from django.utils import timezone
        alerta.reconocida = True
        alerta.reconocida_por = request.user
        alerta.reconocida_en = timezone.now()
        alerta.save(update_fields=["reconocida", "reconocida_por", "reconocida_en"])
        return Response({"status": "reconocida"})
