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
