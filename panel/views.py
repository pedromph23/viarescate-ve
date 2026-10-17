"""Vistas del panel de administración público."""
from django.contrib import messages
from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from operaciones.models import (
    AlertaPredictiva,
    CentroAyuda,
    Inventario,
    Mision,
    Necesidad,
    PrediccionDemanda,
    PrediccionMision,
    Refugio,
    ReporteVial,
    Vehiculo,
    Via,
)
from usuarios.models import Usuario

from .decorators import panel_required, permiso_requerido


def _get_estados_centroides():
    """Devuelve dict {id: {lat, lng}} de estados con centroide definido."""
    from core.models import Estado
    return {
        str(e.id): {"lat": e.centroide_lat, "lng": e.centroide_lng}
        for e in Estado.objects.exclude(centroide_lat__isnull=True)
                                .exclude(centroide_lng__isnull=True)
    }
from .forms import CentroAyudaForm, RefugioForm
from .forms_reporte import ReporteVialForm
from .forms_via import ViaForm


@panel_required
def dashboard(request):
    ahora = timezone.now()
    contexto = {
        "total_centros": CentroAyuda.objects.count(),
        "centros_activos": CentroAyuda.objects.filter(activo=True).count(),
        "total_refugios": Refugio.objects.count(),
        "refugios_activos": Refugio.objects.filter(activo=True).count(),
        "total_usuarios": Usuario.objects.count(),
        "usuarios_activos": Usuario.objects.filter(is_active=True).count(),
        "vias_activas": Via.objects.filter(activa=True).count(),
        "vias_cerradas": Via.objects.filter(estado_vial="CERRADA").count(),
        "incidencias_activas": ReporteVial.objects.filter(
            estado_reporte__in=["PENDIENTE", "CONFIRMADO"]
        ).count(),
        "vehiculos_disponibles": Vehiculo.objects.filter(
            activo=True, estado_operativo="DISPONIBLE"
        ).count(),
        "misiones_en_ruta": Mision.objects.filter(estado_mision="EN_RUTA").count(),
        "inventario_bajo": Inventario.objects.filter(cantidad__lt=F("minimo")).count(),
        "alertas_predictivas": AlertaPredictiva.objects.filter(activa=True).count(),
        "alertas_criticas": AlertaPredictiva.objects.filter(
            activa=True, severidad="CRITICA"
        ).count(),
        "misiones_en_riesgo": PrediccionMision.objects.filter(
            nivel_riesgo__in=["ALTO", "CRITICO"]
        ).count(),
        "ahora": ahora,
    }
    return render(request, "panel/dashboard.html", contexto)


# ---------- CENTROS ----------
@permiso_requerido("ver_centros")
def centros_lista(request):
    q = request.GET.get("q", "").strip()
    qs = CentroAyuda.objects.select_related("estado", "municipio", "parroquia")
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(direccion__icontains=q))
    return render(request, "panel/centros/lista.html", {"centros": qs, "q": q})


@permiso_requerido("crear_centros")
def centros_form(request, pk=None):
    instance = get_object_or_404(CentroAyuda, pk=pk) if pk else None
    if request.method == "POST":
        form = CentroAyudaForm(request.POST, instance=instance)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f"Centro '{obj.nombre}' guardado correctamente.")
            return redirect("panel:centros_lista")
    else:
        form = CentroAyudaForm(instance=instance)
    return render(
        request,
        "panel/centros/form.html",
        {
            "form": form,
            "instance": instance,
            "titulo": "Editar centro" if instance else "Nuevo centro",
            "estados_centroides": _get_estados_centroides(),
        },
    )


@permiso_requerido("eliminar_centros")
def centros_eliminar(request, pk):
    obj = get_object_or_404(CentroAyuda, pk=pk)
    if request.method == "POST":
        nombre = obj.nombre
        obj.delete()
        messages.success(request, f"Centro '{nombre}' eliminado.")
        return redirect("panel:centros_lista")
    return render(request, "panel/confirmar_eliminar.html", {"obj": obj, "tipo": "centro"})


# ---------- REFUGIOS ----------
@permiso_requerido("ver_refugios")
def refugios_lista(request):
    q = request.GET.get("q", "").strip()
    qs = Refugio.objects.select_related("estado", "municipio", "parroquia")
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(direccion__icontains=q))
    return render(request, "panel/refugios/lista.html", {"refugios": qs, "q": q})


@permiso_requerido("crear_refugios")
def refugios_form(request, pk=None):
    instance = get_object_or_404(Refugio, pk=pk) if pk else None
    if request.method == "POST":
        form = RefugioForm(request.POST, instance=instance)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f"Refugio '{obj.nombre}' guardado correctamente.")
            return redirect("panel:refugios_lista")
    else:
        form = RefugioForm(instance=instance)
    return render(
        request,
        "panel/refugios/form.html",
        {
            "form": form,
            "instance": instance,
            "titulo": "Editar refugio" if instance else "Nuevo refugio",
            "estados_centroides": _get_estados_centroides(),
        },
    )


@permiso_requerido("eliminar_refugios")
def refugios_eliminar(request, pk):
    obj = get_object_or_404(Refugio, pk=pk)
    if request.method == "POST":
        nombre = obj.nombre
        obj.delete()
        messages.success(request, f"Refugio '{nombre}' eliminado.")
        return redirect("panel:refugios_lista")
    return render(request, "panel/confirmar_eliminar.html", {"obj": obj, "tipo": "refugio"})


# ---------- USUARIOS (solo lectura + activar/desactivar) ----------
@permiso_requerido("ver_usuarios")
def usuarios_lista(request):
    q = request.GET.get("q", "").strip()
    qs = Usuario.objects.all().order_by("username")
    if q:
        qs = qs.filter(
            Q(username__icontains=q) | Q(email__icontains=q) | Q(first_name__icontains=q)
        )
    return render(request, "panel/usuarios/lista.html", {"usuarios": qs, "q": q})


@permiso_requerido("editar_usuarios")
def usuarios_toggle(request, pk):
    if request.method != "POST":
        return redirect("panel:usuarios_lista")
    user = get_object_or_404(Usuario, pk=pk)
    if user == request.user:
        messages.error(request, "No puede desactivar su propia cuenta.")
        return redirect("panel:usuarios_lista")
    user.is_active = not user.is_active
    user.save(update_fields=["is_active"])
    messages.success(
        request,
        f"Usuario '{user.username}' {'activado' if user.is_active else 'desactivado'}.",
    )
    return redirect("panel:usuarios_lista")


# ---------- VIAS ----------
@permiso_requerido("ver_vias")
def vias_lista(request):
    """Listado de vías con filtros."""
    qs = Via.objects.select_related("estado").order_by("-actualizado_en")

    estado = request.GET.get("estado", "").strip()
    estado_vial = request.GET.get("estado_vial", "").strip()
    q = request.GET.get("q", "").strip()

    if estado:
        qs = qs.filter(estado_id=estado)
    if estado_vial:
        qs = qs.filter(estado_vial=estado_vial)
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(codigo__icontains=q))

    from core.models import Estado
    contexto = {
        "vias": qs,
        "q": q,
        "estado_filtro": estado,
        "estado_vial_filtro": estado_vial,
        "estados_territoriales": Estado.objects.all(),
        "estados_viales": Via.Estados.choices,
    }
    return render(request, "panel/vias/lista.html", contexto)


@permiso_requerido("crear_vias")
def vias_form(request, pk=None):
    """Crear/editar vía."""
    instance = get_object_or_404(Via, pk=pk) if pk else None

    if request.method == "POST":
        form = ViaForm(request.POST, instance=instance)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f"Vía '{obj.nombre}' guardada correctamente.")
            return redirect("panel:vias_lista")
    else:
        form = ViaForm(instance=instance)

    return render(
        request,
        "panel/vias/form.html",
        {
            "form": form,
            "instance": instance,
            "titulo": "Editar vía" if instance else "Nueva vía",
        },
    )


@permiso_requerido("eliminar_vias")
def vias_eliminar(request, pk):
    """Confirmar eliminación de vía."""
    obj = get_object_or_404(Via, pk=pk)
    if request.method == "POST":
        nombre = obj.nombre
        obj.delete()
        messages.success(request, f"Vía '{nombre}' eliminada.")
        return redirect("panel:vias_lista")
    return render(
        request,
        "panel/confirmar_eliminar.html",
        {"obj": obj, "tipo": "vía"},
    )


# ---------- REPORTES (solo lectura) ----------
@permiso_requerido("ver_reportes")
def reportes_lista(request):
    """Listado de reportes viales con filtros."""
    qs = ReporteVial.objects.select_related("via").order_by("-reportado_en")

    # Filtros
    tipo = request.GET.get("tipo", "").strip()
    estado = request.GET.get("estado", "").strip()
    severidad = request.GET.get("severidad", "").strip()
    q = request.GET.get("q", "").strip()

    if tipo:
        qs = qs.filter(tipo=tipo)
    if estado:
        qs = qs.filter(estado_reporte=estado)
    if severidad:
        qs = qs.filter(severidad=severidad)
    if q:
        qs = qs.filter(Q(titulo__icontains=q) | Q(descripcion__icontains=q))

    contexto = {
        "reportes": qs[:300],
        "q": q,
        "tipo_filtro": tipo,
        "estado_filtro": estado,
        "severidad_filtro": severidad,
        "tipos": ReporteVial.Tipos.choices,
        "estados": ReporteVial.Estados.choices,
    }
    return render(request, "panel/reportes/lista.html", contexto)


@permiso_requerido("crear_reportes")
def reportes_form(request, pk=None):
    """Crear/editar reporte vial desde el panel."""
    instance = get_object_or_404(ReporteVial, pk=pk) if pk else None

    if request.method == "POST":
        form = ReporteVialForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            if not obj.reportado_por_id:
                obj.reportado_por = request.user
            obj.save()
            messages.success(request, f"Reporte '{obj.titulo}' guardado correctamente.")
            return redirect("panel:reportes_lista")
    else:
        form = ReporteVialForm(instance=instance)

    return render(
        request,
        "panel/reportes/form.html",
        {
            "form": form,
            "instance": instance,
            "titulo": "Editar reporte" if instance else "Nuevo reporte",
            "estados_centroides": _get_estados_centroides(),
        },
    )


@permiso_requerido("eliminar_reportes")
def reportes_eliminar(request, pk):
    """Confirmar eliminación de reporte."""
    obj = get_object_or_404(ReporteVial, pk=pk)
    if request.method == "POST":
        titulo = obj.titulo
        obj.delete()
        messages.success(request, f"Reporte '{titulo}' eliminado.")
        return redirect("panel:reportes_lista")
    return render(
        request,
        "panel/confirmar_eliminar.html",
        {"obj": obj, "tipo": "reporte"},
    )


# ---------- NECESIDADES ----------
@permiso_requerido("ver_necesidades")
def necesidades_lista(request):
    """Listado de necesidades humanitarias activas."""
    q = request.GET.get("q", "").strip()
    prioridad = request.GET.get("prioridad", "").strip()
    estado = request.GET.get("estado", "").strip()

    qs = Necesidad.objects.select_related(
        "refugio", "recurso", "refugio__estado", "refugio__municipio"
    )

    if q:
        qs = qs.filter(
            Q(refugio__nombre__icontains=q)
            | Q(recurso__nombre__icontains=q)
            | Q(observaciones__icontains=q)
        )
    if prioridad:
        qs = qs.filter(prioridad=prioridad)
    if estado:
        qs = qs.filter(estado=estado)

    contexto = {
        "necesidades": qs,
        "q": q,
        "prioridad_filtro": prioridad,
        "estado_filtro": estado,
        "prioridades": Necesidad.Prioridades.choices,
        "estados": Necesidad.Estados.choices,
    }
    return render(request, "panel/necesidades/lista.html", contexto)


@permiso_requerido("crear_necesidades")
def necesidades_form(request, pk=None):
    """Crear/editar necesidad."""
    from .forms_necesidad import NecesidadForm

    instance = get_object_or_404(Necesidad, pk=pk) if pk else None

    if request.method == "POST":
        form = NecesidadForm(request.POST, instance=instance)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f"Necesidad de '{obj.recurso.nombre}' guardada.")
            return redirect("panel:necesidades_lista")
    else:
        form = NecesidadForm(instance=instance)

    return render(
        request,
        "panel/necesidades/form.html",
        {
            "form": form,
            "instance": instance,
            "titulo": "Editar necesidad" if instance else "Nueva necesidad",
        },
    )


@permiso_requerido("eliminar_necesidades")
def necesidades_eliminar(request, pk):
    """Confirmar eliminación."""
    obj = get_object_or_404(Necesidad, pk=pk)
    if request.method == "POST":
        descripcion = str(obj)
        obj.delete()
        messages.success(request, f"Necesidad eliminada: {descripcion}")
        return redirect("panel:necesidades_lista")
    return render(
        request,
        "panel/confirmar_eliminar.html",
        {"obj": obj, "tipo": "necesidad"},
    )


# ---------- ALERTAS PREDICTIVAS / IA ----------
@permiso_requerido("ver_alertas")
def alertas_lista(request):
    """Listado de alertas predictivas activas."""
    qs = AlertaPredictiva.objects.filter(activa=True).select_related(
        "refugio", "recurso", "mision"
    )
    return render(request, "panel/alertas/lista.html", {"alertas": qs})


@permiso_requerido("reconocer_alertas")
def alertas_reconocer(request, pk):
    """Marca una alerta como reconocida."""
    if request.method != "POST":
        return redirect("panel:alertas_lista")
    obj = get_object_or_404(AlertaPredictiva, pk=pk)
    from django.utils import timezone as tz
    obj.reconocida = True
    obj.reconocida_por = request.user
    obj.reconocida_en = tz.now()
    obj.save(update_fields=["reconocida", "reconocida_por", "reconocida_en"])
    messages.success(request, "Alerta reconocida.")
    return redirect("panel:alertas_lista")


@permiso_requerido("ver_predicciones")
def predicciones_demanda(request):
    """Listado de predicciones de demanda."""
    qs = PrediccionDemanda.objects.select_related(
        "refugio", "recurso"
    ).order_by("-confianza", "-generado_en")
    return render(request, "panel/predicciones/demanda.html", {"predicciones": qs})


@permiso_requerido("ver_predicciones")
def predicciones_misiones(request):
    """Listado de predicciones de misión."""
    qs = PrediccionMision.objects.select_related("mision").order_by(
        "-probabilidad_retraso"
    )
    return render(request, "panel/predicciones/misiones.html", {"predicciones": qs})


# ===========================================================================
# GESTIÓN DE USUARIOS — jerarquía de roles
# ===========================================================================
from .forms_usuario import UsuarioCrearForm, UsuarioEditarForm
from .user_hierarchy import (
    puede_crear_usuario,
    puede_eliminar_usuario,
    puede_modificar_usuario,
)


@permiso_requerido("crear_usuarios")
def usuarios_form(request, pk=None):
    """Crear o editar usuario. Con reglas de jerarquía."""
    target = get_object_or_404(Usuario, pk=pk) if pk else None
    es_edicion = target is not None

    if es_edicion and not puede_modificar_usuario(request.user, target):
        messages.error(
            request,
            "No tiene permiso para editar a este usuario."
        )
        return redirect("panel:usuarios_lista")

    if request.method == "POST":
        FormClass = UsuarioEditarForm if es_edicion else UsuarioCrearForm
        form = FormClass(request.POST, instance=target, gestor=request.user)

        if form.is_valid():
            rol_solicitado = form.cleaned_data.get("rol")
            if not puede_crear_usuario(request.user, rol_solicitado):
                messages.error(
                    request,
                    f"No puede asignar el rol '{rol_solicitado}' "
                    "(excede su nivel jerárquico)."
                )
            else:
                user = form.save()
                accion = "actualizado" if es_edicion else "creado"
                messages.success(
                    request,
                    f"Usuario '{user.username}' {accion} correctamente.",
                )
                return redirect("panel:usuarios_lista")
    else:
        FormClass = UsuarioEditarForm if es_edicion else UsuarioCrearForm
        form = FormClass(instance=target, gestor=request.user)

    return render(
        request,
        "panel/usuarios/form.html",
        {
            "form": form,
            "instance": target,
            "titulo": (
                f"Editar usuario: {target.username}"
                if es_edicion
                else "Nuevo usuario"
            ),
        },
    )


@permiso_requerido("eliminar_usuarios")
def usuarios_eliminar(request, pk):
    """Eliminar usuario con jerarquía (y nunca al último admin)."""
    target = get_object_or_404(Usuario, pk=pk)

    if not puede_eliminar_usuario(request.user, target):
        messages.error(
            request,
            "No tiene permiso para eliminar a este usuario "
            "(jerarquía, es su propia cuenta o es el último administrador)."
        )
        return redirect("panel:usuarios_lista")

    if request.method == "POST":
        username = target.username
        target.delete()
        messages.success(request, f"Usuario '{username}' eliminado.")
        return redirect("panel:usuarios_lista")

    return render(
        request,
        "panel/confirmar_eliminar.html",
        {"obj": target, "tipo": "usuario"},
    )
