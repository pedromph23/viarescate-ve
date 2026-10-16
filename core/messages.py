"""Mensajes de error centralizados — VíaRescate VE."""

# Generales
CAMPO_OBLIGATORIO = "Este campo es obligatorio."
SOLO_ESPACIOS = "El campo no puede contener solo espacios."

# Nombres propios
NOMBRE_INVALIDO = "El nombre solo puede contener letras, espacios, guiones y apóstrofes."
NOMBRE_MUY_CORTO = "El nombre debe tener al menos 3 caracteres."
NOMBRE_MUY_LARGO = "El nombre no puede superar los 120 caracteres."
NOMBRE_CON_NUMEROS = "El nombre no puede contener números ni símbolos."
NOMBRE_REPETIDO = "El nombre contiene caracteres repetidos de forma no válida."

# Email
EMAIL_INVALIDO = "El correo electrónico no es válido."
EMAIL_DUPLICADO = "Ya existe una cuenta con este correo electrónico."

# Teléfono
TELEFONO_INVALIDO = "El teléfono debe tener el formato +58XXXXXXXXXX (11 dígitos)."
TELEFONO_PREFIJO_INVALIDO = "El prefijo del teléfono no es válido para Venezuela."

# Cédula / RIF
CEDULA_INVALIDA = "La cédula debe tener el formato V-12345678."
CEDULA_DUPLICADA = "Ya existe un usuario con esta cédula."
RIF_INVALIDO = "El RIF debe tener el formato J-12345678-9."
RIF_DUPLICADO = "Ya existe un registro con este RIF."

# Coordenadas
COORDENADAS_FUERA_VE = "La ubicación está fuera de Venezuela."
COORDENADAS_INVALIDAS = "Las coordenadas no son válidas."

# Territorial
ESTADO_INVALIDO = "Seleccione un estado válido."
MUNICIPIO_NO_PERTENECE = "El municipio no pertenece al estado seleccionado."
PARROQUIA_NO_PERTENECE = "La parroquia no pertenece al municipio seleccionado."

# Cantidades
CANTIDAD_NEGATIVA = "La cantidad no puede ser negativa."
CANTIDAD_EXCESIVA = "La cantidad ingresada es demasiado alta."
OCUPACION_MAYOR_CAPACIDAD = "La ocupación no puede superar la capacidad."

# Fechas
FECHA_PASADO = "La fecha no puede estar en el pasado."
FECHA_ENTREGA_ANTES = "La fecha de entrega no puede ser anterior a la de salida."

# Código interno
CODIGO_INVALIDO = "El código debe empezar con letra y contener solo mayúsculas, números y guiones bajos."
CODIGO_DUPLICADO = "Ya existe un registro con este código."

# Placa
PLACA_INVALIDA = "La placa no tiene un formato válido."

# Dirección
DIRECCION_INVALIDA = "La dirección debe contener al menos una letra y un número."

# Autenticación
CREDENCIALES_INVALIDAS = "Usuario o contraseña incorrectos."
SIN_PERMISO = "No tiene permisos para acceder a esta sección."

# Fechas (Fase G)
FECHA_ENTREGA_ANTES_SALIDA = "La fecha de entrega estimada no puede ser anterior a la salida."
FECHA_ENTREGA_REAL_ANTES_SALIDA = "La fecha de entrega real no puede ser anterior a la salida."
FECHA_RESOLUCION_ANTES_REPORTE = "La fecha de resolución no puede ser anterior al reporte."
FECHA_CENSO_FUTURA = "La fecha del último censo no puede ser futura."
FECHA_SALIDA_PASADA = "La fecha de salida planificada no puede estar en el pasado."

# Necesidad
NECESIDAD_CANTIDAD_INVALIDA = "La cantidad requerida debe ser mayor que cero."
NECESIDAD_RECIBIDA_EXCEDE = "La cantidad recibida no puede superar la requerida."
NECESIDAD_FECHA_PASADA = "La fecha requerida no puede estar en el pasado."
NECESIDAD_DUPLICADA = "Ya existe una necesidad registrada para este recurso en este refugio."
NECESIDAD_ESTADO_INCOHERENTE = "El estado no es coherente con las cantidades registradas."
