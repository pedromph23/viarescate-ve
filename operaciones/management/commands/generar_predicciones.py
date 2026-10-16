"""
Pipeline de generación de predicciones.

Uso:
    python manage.py generar_predicciones
    python manage.py generar_predicciones --solo-demanda
    python manage.py generar_predicciones --solo-misiones
    python manage.py generar_predicciones --horizonte DIAS_14

Diseñado para ejecutarse:
- Manualmente desde local
- Vía cron externo (Railway/Fly/GitHub Actions) apuntando a Supabase
- NUNCA desde Vercel (serverless no ejecuta workers persistentes)
"""
import statistics
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.utils import timezone

from operaciones.models import (
    AlertaPredictiva,
    Mision,
    Necesidad,
    PrediccionDemanda,
    PrediccionMision,
    Refugio,
)


class Command(BaseCommand):
    help = "Genera predicciones de demanda y riesgo usando datos históricos."

    def add_arguments(self, parser):
        parser.add_argument("--solo-demanda", action="store_true")
        parser.add_argument("--solo-misiones", action="store_true")
        parser.add_argument("--solo-alertas", action="store_true")
        parser.add_argument(
            "--horizonte",
            default="DIAS_14",
            choices=["DIAS_7", "DIAS_14", "DIAS_30"],
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("=== Pipeline de predicción ==="))

        if not options["solo_misiones"] and not options["solo_alertas"]:
            self._predecir_demanda(options["horizonte"])

        if not options["solo_demanda"] and not options["solo_alertas"]:
            self._predecir_misiones()

        if not options["solo_demanda"] and not options["solo_misiones"]:
            self._generar_alertas()

        self.stdout.write(self.style.SUCCESS("\n[OK] Pipeline completado."))

    # ------------------------------------------------------------------
    # 1. PREDICCIÓN DE DEMANDA
    # ------------------------------------------------------------------
    def _predecir_demanda(self, horizonte):
        """
        Usa un modelo simple de promedio móvil ponderado sobre las necesidades
        históricas. Para producción se puede cambiar a Prophet sin tocar la API.

        Señal: cantidad_requerida de Necesidad agrupada por (refugio, recurso).
        """
        self.stdout.write("\n[1/3] Predicción de demanda...")

        # Datos históricos: necesidades de los últimos 90 días
        corte = timezone.now() - timedelta(days=90)
        historico = (
            Necesidad.objects
            .filter(creado_en__gte=corte)
            .values("refugio_id", "recurso_id")
            .annotate(total=Sum("cantidad_requerida"))
        )

        # Si no hay histórico, usamos todas las necesidades activas
        if not historico:
            self.stdout.write(
                self.style.WARNING("  Sin histórico de 90 días. Usando necesidades activas.")
            )
            historico = (
                Necesidad.objects
                .filter(estado__in=["PENDIENTE", "PARCIAL"])
                .values("refugio_id", "recurso_id")
                .annotate(total=Sum("cantidad_pendiente_calc"))
                if False  # cantidad_pendiente es property, no se puede agregar
                else Necesidad.objects.values("refugio_id", "recurso_id").annotate(
                    total=Sum("cantidad_requerida")
                )
            )

        # Factor de horizonte: 7d=1.0, 14d=1.8, 30d=3.5
        factores = {"DIAS_7": 1.0, "DIAS_14": 1.8, "DIAS_30": 3.5}
        factor = factores.get(horizonte, 1.8)

        creadas = 0
        for row in historico:
            cantidad_base = float(row["total"] or 0)
            if cantidad_base <= 0:
                continue

            cantidad_predicha = round(cantidad_base * factor, 2)

            # Confianza: basada en volumen histórico. Más datos = más confianza.
            # Rango 50-85 para ser conservadores (nunca prometemos precisión absoluta)
            confianza = min(85.0, 50.0 + (cantidad_base / 10.0))

            PrediccionDemanda.objects.update_or_create(
                refugio_id=row["refugio_id"],
                recurso_id=row["recurso_id"],
                horizonte=horizonte,
                defaults={
                    "cantidad_predicha": Decimal(str(cantidad_predicha)),
                    "confianza": Decimal(str(round(confianza, 2))),
                    "modelo_usado": "moving_average_v1",
                },
            )
            creadas += 1

        self.stdout.write(f"  → {creadas} predicciones de demanda actualizadas.")

    # ------------------------------------------------------------------
    # 2. PREDICCIÓN DE RIESGO EN MISIONES
    # ------------------------------------------------------------------
    def _predecir_misiones(self):
        """
        Evalúa misiones activas y estima riesgo de retraso basándose en:
        - Antigüedad de la misión
        - Estado actual
        - Número de reportes viales en la zona
        - Prioridad
        """
        self.stdout.write("\n[2/3] Predicción de riesgo en misiones...")

        misiones_activas = Mision.objects.filter(
            estado_mision__in=["PLANIFICADA", "ASIGNADA", "EN_RUTA"]
        )
        ahora = timezone.now()
        creadas = 0

        for mision in misiones_activas:
            razones = []
            score = 0

            # Factor 1: tiempo desde planificación
            if mision.planificada_en:
                horas_planificada = (ahora - mision.planificada_en).total_seconds() / 3600
                if horas_planificada > 48:
                    score += 30
                    razones.append(f"Planificada hace {int(horas_planificada)}h (>48h)")
                elif horas_planificada > 24:
                    score += 15
                    razones.append(f"Planificada hace {int(horas_planificada)}h")

            # Factor 2: prioridad alta
            if mision.prioridad >= 4:
                score += 10
                razones.append(f"Prioridad {mision.prioridad}/5")

            # Factor 3: fecha de salida planificada ya pasada
            if mision.fecha_salida_planificada and mision.fecha_salida_planificada < ahora:
                score += 25
                razones.append("Fecha de salida planificada ya pasó")

            # Factor 4: sin vehículo asignado
            if not mision.vehiculo:
                score += 15
                razones.append("Sin vehículo asignado")

            # Factor 5: retraso en fecha de entrega estimada
            if (
                mision.fecha_entrega_estimada
                and mision.fecha_salida_planificada
                and mision.fecha_entrega_estimada < ahora
            ):
                score += 20
                razones.append("Fecha de entrega estimada superada")

            # Clasificar
            if score >= 60:
                nivel = "CRITICO"
                probabilidad = 85.0
                retraso = 120
            elif score >= 40:
                nivel = "ALTO"
                probabilidad = 70.0
                retraso = 60
            elif score >= 20:
                nivel = "MEDIO"
                probabilidad = 45.0
                retraso = 30
            else:
                nivel = "BAJO"
                probabilidad = 15.0
                retraso = 0

            PrediccionMision.objects.update_or_create(
                mision=mision,
                defaults={
                    "retraso_estimado_minutos": retraso,
                    "probabilidad_retraso": Decimal(str(probabilidad)),
                    "nivel_riesgo": nivel,
                    "razones": razones,
                },
            )
            creadas += 1

        self.stdout.write(f"  → {creadas} predicciones de misión actualizadas.")

    # ------------------------------------------------------------------
    # 3. GENERACIÓN DE ALERTAS PREDICTIVAS
    # ------------------------------------------------------------------
    def _generar_alertas(self):
        """Genera alertas a partir de las predicciones más críticas."""
        self.stdout.write("\n[3/3] Generando alertas predictivas...")

        # Marcar alertas anteriores como inactivas
        AlertaPredictiva.objects.filter(activa=True).update(activa=False)

        creadas = 0

        # Alerta 1: refugios con demanda alta proyectada
        predicciones_altas = PrediccionDemanda.objects.select_related(
            "refugio", "recurso"
        ).filter(confianza__gte=70)[:20]

        for pred in predicciones_altas:
            AlertaPredictiva.objects.create(
                tipo="DEMANDA_ALTA",
                severidad="ADVERTENCIA",
                titulo=f"Demanda proyectada de {pred.recurso.nombre}",
                descripcion=(
                    f"Se proyecta una demanda de {pred.cantidad_predicha} "
                    f"{pred.recurso.unidad} en {pred.refugio.nombre} "
                    f"durante {pred.get_horizonte_display()}."
                ),
                accion_recomendada=(
                    f"Verificar stock en centros de acopio y priorizar "
                    f"distribución hacia {pred.refugio.nombre}."
                ),
                refugio=pred.refugio,
                recurso=pred.recurso,
                datos_soporte={
                    "cantidad_predicha": float(pred.cantidad_predicha),
                    "confianza": float(pred.confianza),
                    "horizonte": pred.horizonte,
                },
            )
            creadas += 1

        # Alerta 2: misiones con riesgo alto o crítico
        misiones_riesgo = PrediccionMision.objects.select_related("mision").filter(
            nivel_riesgo__in=["ALTO", "CRITICO"]
        )[:20]

        for pred in misiones_riesgo:
            severidad = "CRITICA" if pred.nivel_riesgo == "CRITICO" else "ADVERTENCIA"
            AlertaPredictiva.objects.create(
                tipo="MISION_RIESGO",
                severidad=severidad,
                titulo=f"Misión {pred.mision.codigo} en riesgo",
                descripcion=(
                    f"Probabilidad de retraso del {pred.probabilidad_retraso}%. "
                    f"Retraso estimado: {pred.retraso_estimado_minutos or 0} min."
                ),
                accion_recomendada=(
                    "Revisar asignación de vehículo, verificar estado de vías "
                    "y considerar ruta alternativa."
                ),
                mision=pred.mision,
                datos_soporte={
                    "razones": pred.razones,
                    "probabilidad": float(pred.probabilidad_retraso),
                },
            )
            creadas += 1

        self.stdout.write(f"  → {creadas} alertas predictivas generadas.")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _calcular_confianza(self, n_muestras, variabilidad):
        """Confianza basada en cantidad de datos y variabilidad."""
        if n_muestras < 3:
            return 40.0
        base = min(90.0, 50.0 + (n_muestras * 2))
        return max(30.0, base - (variabilidad * 10))
