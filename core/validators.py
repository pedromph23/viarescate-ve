"""Validadores reutilizables — VíaRescate VE."""
import re

from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator

from . import messages as msg

RE_NOMBRE = re.compile(
    r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+(?:[ '\-][A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)*$"
)
RE_CODIGO = re.compile(r"^[A-Z][A-Z0-9_]{2,29}$")
RE_CEDULA = re.compile(r"^[VEJP]-\d{6,9}$")
RE_RIF = re.compile(r"^[JVEGP]-\d{8}-\d$")
RE_TELEFONO_VE = re.compile(r"^\+58(4\d{9}|2\d{9})$")
RE_PLACA = re.compile(
    r"^([A-Z]{2}\d{3}[A-Z]{2}|[A-Z]\d{3}[A-Z]{3}|\d{4}[A-Z]{2}|[A-Z]{2}\d{4})$"
)

PREFIJOS_MOVIL_VE = ("412", "414", "416", "424", "426")

VE_LAT_MIN, VE_LAT_MAX = 0.6, 12.3
VE_LNG_MIN, VE_LNG_MAX = -73.4, -59.8


def _normalizar(texto):
    if not texto:
        return ""
    return re.sub(r"\s+", " ", str(texto).strip())


def validar_nombre_propio(valor):
    valor = _normalizar(valor)
    if not valor:
        raise ValidationError(msg.CAMPO_OBLIGATORIO)
    if len(valor) < 3:
        raise ValidationError(msg.NOMBRE_MUY_CORTO)
    if len(valor) > 120:
        raise ValidationError(msg.NOMBRE_MUY_LARGO)
    if any(c.isdigit() for c in valor):
        raise ValidationError(msg.NOMBRE_CON_NUMEROS)
    if not RE_NOMBRE.match(valor):
        raise ValidationError(msg.NOMBRE_INVALIDO)
    if re.search(r"([BbCcDdFfGgHhJjKkLlMmNnPpQqRrSsTtVvWwXxYyZz])\1{2,}", valor):
        raise ValidationError(msg.NOMBRE_REPETIDO)
    letras = {c.lower() for c in valor if c.isalpha()}
    if len(letras) < 2:
        raise ValidationError(msg.NOMBRE_REPETIDO)
    return valor


def validar_email(valor):
    valor = (valor or "").strip().lower()
    EmailValidator(msg.EMAIL_INVALIDO)(valor)
    return valor


def normalizar_telefono_ve(valor):
    if not valor:
        raise ValidationError(msg.CAMPO_OBLIGATORIO)
    limpio = re.sub(r"[\s\-\(\)\.]", "", str(valor))
    if limpio.startswith("0"):
        limpio = limpio[1:]
    if limpio.startswith("58"):
        limpio = "+" + limpio
    elif not limpio.startswith("+"):
        limpio = "+58" + limpio
    if not RE_TELEFONO_VE.match(limpio):
        raise ValidationError(msg.TELEFONO_INVALIDO)
    prefijo = limpio[3:6]
    if prefijo.startswith("4") and prefijo not in PREFIJOS_MOVIL_VE:
        raise ValidationError(msg.TELEFONO_PREFIJO_INVALIDO)
    return limpio


def validar_cedula_ve(valor):
    valor = (valor or "").strip().upper()
    if not RE_CEDULA.match(valor):
        raise ValidationError(msg.CEDULA_INVALIDA)
    return valor


def validar_rif(valor):
    valor = (valor or "").strip().upper()
    if not RE_RIF.match(valor):
        raise ValidationError(msg.RIF_INVALIDO)
    return valor


def validar_codigo_interno(valor):
    valor = (valor or "").strip().upper()
    if not valor:
        raise ValidationError(msg.CAMPO_OBLIGATORIO)
    if not RE_CODIGO.match(valor):
        raise ValidationError(msg.CODIGO_INVALIDO)
    return valor


def validar_placa_ve(valor):
    valor = re.sub(r"[\s\-]", "", (valor or "")).upper()
    if not RE_PLACA.match(valor):
        raise ValidationError(msg.PLACA_INVALIDA)
    return valor


def validar_coordenadas_ve(lat, lng):
    try:
        lat = float(lat)
        lng = float(lng)
    except (TypeError, ValueError):
        raise ValidationError(msg.COORDENADAS_INVALIDAS)
    if not (VE_LAT_MIN <= lat <= VE_LAT_MAX):
        raise ValidationError(msg.COORDENADAS_FUERA_VE)
    if not (VE_LNG_MIN <= lng <= VE_LNG_MAX):
        raise ValidationError(msg.COORDENADAS_FUERA_VE)
    if lat == 0 and lng == 0:
        raise ValidationError(msg.COORDENADAS_INVALIDAS)
    return lat, lng


def validar_cantidad(valor, maximo=1_000_000):
    try:
        n = int(valor)
    except (TypeError, ValueError):
        raise ValidationError(msg.CANTIDAD_NEGATIVA)
    if n < 0:
        raise ValidationError(msg.CANTIDAD_NEGATIVA)
    if n > maximo:
        raise ValidationError(msg.CANTIDAD_EXCESIVA)
    return n


# ---------------------------------------------------------------------------
# Validadores de fechas (Fase G)
# ---------------------------------------------------------------------------
from datetime import date, datetime, timedelta

from django.utils import timezone


# Margen de tolerancia para evitar rechazos por drift de reloj.
# 60 segundos es imperceptible para el usuario pero absorbe latencia,
# desfase cliente-servidor y microsegundos entre timezone.now() consecutivos.
_GRACE = timedelta(seconds=60)


def validar_fecha_no_pasada(valor, mensaje=None):
    """Rechaza fechas anteriores a hoy/ahora (con margen de 60s)."""
    if valor is None:
        return valor
    if isinstance(valor, datetime):
        limite = timezone.now() - _GRACE
    else:
        limite = date.today() - timedelta(days=1)
    if valor < limite:
        raise ValidationError(mensaje or msg.FECHA_PASADO)
    return valor


def validar_fecha_futura(valor, mensaje=None):
    """Rechaza fechas posteriores a hoy/ahora (con margen de 60s)."""
    if valor is None:
        return valor
    if isinstance(valor, datetime):
        limite = timezone.now() + _GRACE
    else:
        limite = date.today() + timedelta(days=1)
    if valor > limite:
        raise ValidationError(mensaje or msg.FECHA_CENSO_FUTURA)
    return valor


def validar_orden_fechas(fecha_inicio, fecha_fin, mensaje):
    """Verifica que fecha_fin >= fecha_inicio. Ignora si alguna es None."""
    if fecha_inicio is None or fecha_fin is None:
        return
    if fecha_fin < fecha_inicio:
        raise ValidationError(mensaje)



# ---------------------------------------------------------------------------
# Validación de imágenes subidas (fotos de reportes)
# ---------------------------------------------------------------------------
from pathlib import Path as _Path


MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_IMAGE_MIMES = {"image/jpeg", "image/png", "image/webp"}


def validar_imagen_archivo(archivo, mensaje=None):
    """
    Valida un archivo subido como imagen:
    - Extensión permitida (.jpg, .jpeg, .png, .webp)
    - Tamaño ≤ 5 MB
    - MIME permitido (si está disponible)

    NO confía en la extensión sola. El backend (Django ImageField con Pillow)
    verifica que realmente sea una imagen al procesarla.
    """
    if archivo is None:
        return archivo

    # Tamaño
    size = getattr(archivo, "size", 0)
    if size > MAX_IMAGE_SIZE_BYTES:
        max_mb = MAX_IMAGE_SIZE_BYTES // (1024 * 1024)
        raise ValidationError(
            mensaje or f"La imagen supera el tamaño máximo de {max_mb} MB."
        )

    # Extensión
    nombre = getattr(archivo, "name", "")
    ext = _Path(nombre).suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            mensaje or "Formato de imagen no permitido. Use JPG, PNG o WEBP."
        )

    # MIME (puede no estar presente en todos los uploads)
    content_type = getattr(archivo, "content_type", None)
    if content_type and content_type not in ALLOWED_IMAGE_MIMES:
        raise ValidationError(
            mensaje or "El archivo no es una imagen válida."
        )

    return archivo


# ---------------------------------------------------------------------------
# Validadores temporales robustos — anti-inyección de fechas
# ---------------------------------------------------------------------------
def validar_fecha_con_referencia(
    fecha,
    referencia=None,
    grace_minutos=5,
    max_edad_dias=30,
    contexto="incidente",
    permitir_nulo=True,
    solo_hoy=False,
):
    """
    Valida una fecha contra una referencia temporal (default: ahora).

    - grace_minutos: tolerancia para desfase de reloj del cliente
    - max_edad_dias: ventana máxima hacia atrás (solo si solo_hoy=False)
    - solo_hoy: si es True, la fecha debe ser HOY (00:00 hasta ahora+grace)
    - Rechaza naive datetimes (Django siempre debe usar aware)
    """
    if fecha is None:
        if permitir_nulo:
            return None
        raise ValidationError(f"La fecha del {contexto} es obligatoria.")

    # Forzar aware
    if timezone.is_naive(fecha):
        fecha = timezone.make_aware(fecha, timezone.get_current_timezone())

    if referencia is None:
        referencia = timezone.now()
    elif timezone.is_naive(referencia):
        referencia = timezone.make_aware(referencia, timezone.get_current_timezone())

    limite_futuro = referencia + timedelta(minutes=grace_minutos)

    if solo_hoy:
        # Solo se permite: hoy (desde 00:00 hasta ahora + grace)
        # El "inicio del día" depende de la zona horaria local
        limite_pasado = referencia.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(minutes=grace_minutos)
    else:
        limite_pasado = referencia - timedelta(days=max_edad_dias)

    if fecha > limite_futuro:
        raise ValidationError(
            f"La fecha del {contexto} no puede estar en el futuro. "
            f"Máximo {grace_minutos} minutos de tolerancia."
        )

    if fecha < limite_pasado:
        if solo_hoy:
            raise ValidationError(
                f"La fecha del {contexto} debe ser hoy. "
                f"No se pueden reportar incidentes de días anteriores."
            )
        raise ValidationError(
            f"La fecha del {contexto} no puede ser mayor a "
            f"{max_edad_dias} días en el pasado."
        )

    return fecha


def validar_fecha_en_pasado_o_ahora(fecha, grace_minutos=5, contexto="evento"):
    """
    Para fechas que NUNCA pueden ser futuras (iniciada_en, entregada_en,
    cancelada_en, resuelto_en). Rechaza cualquier valor > ahora + grace.
    """
    if fecha is None:
        return None

    if timezone.is_naive(fecha):
        fecha = timezone.make_aware(fecha, timezone.get_current_timezone())

    limite = timezone.now() + timedelta(minutes=grace_minutos)
    if fecha > limite:
        raise ValidationError(
            f"La fecha del {contexto} no puede estar en el futuro. "
            f"Máximo {grace_minutos} minutos de tolerancia."
        )
    return fecha


# ---------------------------------------------------------------------------
# Validadores específicos para usuarios
# ---------------------------------------------------------------------------
RE_USERNAME = re.compile(r"^[a-zA-Z0-9_.-]{3,150}$")
RE_PASSWORD_SIMBOLO = re.compile(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]")

# Palabras prohibidas en contraseñas (lista mínima)
PASSWORDS_PROHIBIDAS = {
    "12345678", "123456789", "password", "qwerty",
    "admin123", "admin1234", "administrador",
    "contraseña", "password123", "1234567890",
    "abc123456", "qwerty123", "venezuela",
}

# Nombres/artículos comunes en Venezuela para permitir en nombres propios
ARTICULOS_NOMBRE = {"de", "del", "la", "las", "los", "el", "y", "san", "santa"}


def validar_username(valor):
    """Username: alfanumérico + _ . -, 3-150 chars, sin empezar con . o -."""
    valor = (valor or "").strip()
    if not valor:
        raise ValidationError(msg.CAMPO_OBLIGATORIO)
    if len(valor) < 3:
        raise ValidationError("El usuario debe tener al menos 3 caracteres.")
    if len(valor) > 150:
        raise ValidationError("El usuario no puede superar 150 caracteres.")
    if valor.startswith((".", "-", "_")):
        raise ValidationError(
            "El usuario no puede empezar con punto, guion o guion bajo."
        )
    if not RE_USERNAME.match(valor):
        raise ValidationError(
            "El usuario solo puede contener letras, números, puntos, "
            "guiones y guiones bajos."
        )
    return valor


def validar_nombre_persona(valor, contexto="nombre"):
    """
    Nombre o apellido de persona. Más permisivo que el de entidades
    (permite artículos como 'de', 'del', 'la', 'los', 'san').
    """
    valor = _normalizar(valor)
    if not valor:
        raise ValidationError(msg.CAMPO_OBLIGATORIO)
    if len(valor) < 2:
        raise ValidationError(f"El {contexto} debe tener al menos 2 caracteres.")
    if len(valor) > 150:
        raise ValidationError(f"El {contexto} no puede superar 150 caracteres.")
    if any(c.isdigit() for c in valor):
        raise ValidationError(f"El {contexto} no puede contener números.")
    if not RE_NOMBRE.match(valor):
        raise ValidationError(
            f"El {contexto} solo puede contener letras, espacios, "
            "guiones y apóstrofes."
        )
    return valor


def validar_password_fuerte(valor, username=None, email=None):
    """
    Contraseña robusta:
    - Mínimo 12 caracteres
    - Al menos 1 mayúscula, 1 minúscula, 1 dígito, 1 símbolo
    - No contiene username ni email
    - No está en la lista de prohibidas
    """
    from django.contrib.auth.password_validation import validate_password

    if not valor:
        raise ValidationError(msg.CAMPO_OBLIGATORIO)

    if len(valor) < 12:
        raise ValidationError("La contraseña debe tener al menos 12 caracteres.")
    if len(valor) > 128:
        raise ValidationError("La contraseña no puede superar 128 caracteres.")
    if not any(c.isupper() for c in valor):
        raise ValidationError("La contraseña debe tener al menos una mayúscula.")
    if not any(c.islower() for c in valor):
        raise ValidationError("La contraseña debe tener al menos una minúscula.")
    if not any(c.isdigit() for c in valor):
        raise ValidationError("La contraseña debe tener al menos un número.")
    if not RE_PASSWORD_SIMBOLO.search(valor):
        raise ValidationError(
            "La contraseña debe tener al menos un símbolo (!@#$%...)."
        )

    # Lista negra
    if valor.lower() in PASSWORDS_PROHIBIDAS:
        raise ValidationError("Esta contraseña es demasiado común. Usa otra.")

    # No contener username/email
    if username and username.lower() in valor.lower() and len(username) >= 4:
        raise ValidationError("La contraseña no puede contener tu nombre de usuario.")
    if email:
        email_user = email.split("@")[0].lower()
        if email_user and len(email_user) >= 4 and email_user in valor.lower():
            raise ValidationError("La contraseña no puede contener tu correo.")

    # Django validators (comunes)
    validate_password(valor, user=None)

    return valor
