"""Vistas del panel de administración público."""
from django.contrib import messages
from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from operaciones.models import (
    CentroAyuda,
    Inventario,
    Mision,
    Refugio,
    ReporteVial,
    Vehiculo,
    Via,
)
from usuarios.models import Usuario

from .decorators import panel_required
from .forms import CentroAyudaForm, RefugioForm


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
        "ahora": ahora,
    }
    return render(request, "panel/dashboard.html", contexto)


# ---------- CENTROS ----------
@panel_required
def centros_lista(request):
    q = request.GET.get("q", "").strip()
    qs = CentroAyuda.objects.select_related("estado", "municipio", "parroquia")
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(direccion__icontains=q))
    return render(request, "panel/centros/lista.html", {"centros": qs, "q": q})


@panel_required
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
        {"form": form, "instance": instance, "titulo": "Editar centro" if instance else "Nuevo centro"},
    )


@panel_required
def centros_eliminar(request, pk):
    obj = get_object_or_404(CentroAyuda, pk=pk)
    if request.method == "POST":
        nombre = obj.nombre
        obj.delete()
        messages.success(request, f"Centro '{nombre}' eliminado.")
        return redirect("panel:centros_lista")
    return render(request, "panel/confirmar_eliminar.html", {"obj": obj, "tipo": "centro"})


# ---------- REFUGIOS ----------
@panel_required
def refugios_lista(request):
    q = request.GET.get("q", "").strip()
    qs = Refugio.objects.select_related("estado", "municipio", "parroquia")
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(direccion__icontains=q))
    return render(request, "panel/refugios/lista.html", {"refugios": qs, "q": q})


@panel_required
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
        {"form": form, "instance": instance, "titulo": "Editar refugio" if instance else "Nuevo refugio"},
    )


@panel_required
def refugios_eliminar(request, pk):
    obj = get_object_or_404(Refugio, pk=pk)
    if request.method == "POST":
        nombre = obj.nombre
        obj.delete()
        messages.success(request, f"Refugio '{nombre}' eliminado.")
        return redirect("panel:refugios_lista")
    return render(request, "panel/confirmar_eliminar.html", {"obj": obj, "tipo": "refugio"})


# ---------- USUARIOS (solo lectura + activar/desactivar) ----------
@panel_required
def usuarios_lista(request):
    q = request.GET.get("q", "").strip()
    qs = Usuario.objects.all().order_by("username")
    if q:
        qs = qs.filter(
            Q(username__icontains=q) | Q(email__icontains=q) | Q(first_name__icontains=q)
        )
    return render(request, "panel/usuarios/lista.html", {"usuarios": qs, "q": q})


@panel_required
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


# ---------- VIAS (solo lectura) ----------
@panel_required
def vias_lista(request):
    qs = Via.objects.select_related("estado").order_by("-actualizado_en")
    return render(request, "panel/vias/lista.html", {"vias": qs})


# ---------- REPORTES (solo lectura) ----------
@panel_required
def reportes_lista(request):
    qs = ReporteVial.objects.select_related("via").order_by("-reportado_en")[:200]
    return render(request, "panel/reportes/lista.html", {"reportes": qs})
