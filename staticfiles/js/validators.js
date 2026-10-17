/**
 * Validaciones en cliente — VíaRescate VE.
 * Espejo de core/validators.py. SOLO UX, el backend revalida todo.
 */
(function () {
    "use strict";

    // Regex — mismo patrón que el backend
    const RE = {
        nombre: /^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+(?:[ '\-][A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)*$/,
        codigo: /^[A-Z][A-Z0-9_]{2,29}$/,
        cedula: /^[VEJP]-\d{6,9}$/,
        rif: /^[JVEGP]-\d{8}-\d$/,
        telefono: /^\+58(4\d{9}|2\d{9})$/,
        placa: /^([A-Z]{2}\d{3}[A-Z]{2}|[A-Z]\d{3}[A-Z]{3}|\d{4}[A-Z]{2}|[A-Z]{2}\d{4})$/,
    };

    const MSG = {
        obligatorio: "Este campo es obligatorio.",
        nombreInvalido: "El nombre solo puede contener letras, espacios, guiones y apóstrofes.",
        nombreCorto: "El nombre debe tener al menos 3 caracteres.",
        nombreNumero: "El nombre no puede contener números ni símbolos.",
        telefono: "El teléfono debe tener el formato +58XXXXXXXXXX.",
        coordenadaFuera: "La ubicación está fuera de Venezuela.",
        fuera: "El valor está fuera de rango permitido.",
    };

    // Normaliza texto antes de validar
    function normalizar(s) {
        return String(s || "").trim().replace(/\s+/g, " ");
    }

    // Validadores por tipo de campo (data-validator)
    const validadores = {

        nombre: function (v) {
            v = normalizar(v);
            if (!v) return MSG.obligatorio;
            if (v.length < 3) return MSG.nombreCorto;
            if (v.length > 120) return "El nombre no puede superar los 120 caracteres.";
            if (/\d/.test(v)) return MSG.nombreNumero;
            if (!RE.nombre.test(v)) return MSG.nombreInvalido;
            const letras = new Set(v.toLowerCase().replace(/[^a-záéíóúüñ]/g, ""));
            if (letras.size < 2) return "El nombre debe tener al menos 2 letras distintas.";
            return null;
        },

        telefono: function (v) {
            if (!v) return null;  // opcional
            let limpio = v.replace(/[\s\-().]/g, "");
            if (limpio.startsWith("0")) limpio = "+58" + limpio.slice(1);
            else if (limpio.startsWith("58")) limpio = "+" + limpio;
            else if (!limpio.startsWith("+")) limpio = "+58" + limpio;
            if (!RE.telefono.test(limpio)) return MSG.telefono;
            return null;
        },

        email: function (v) {
            if (!v) return null;
            if (v.length > 254) return "El correo es demasiado largo.";
            if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v)) {
                return "El correo electrónico no es válido.";
            }
            return null;
        },

        cedula: function (v) {
            if (!v) return null;
            if (!RE.cedula.test(v.toUpperCase())) {
                return "La cédula debe tener el formato V-12345678.";
            }
            return null;
        },

        rif: function (v) {
            if (!v) return null;
            if (!RE.rif.test(v.toUpperCase())) {
                return "El RIF debe tener el formato J-12345678-9.";
            }
            return null;
        },

        codigo: function (v) {
            if (!v) return MSG.obligatorio;
            if (!RE.codigo.test(v.toUpperCase())) {
                return "El código debe empezar con letra mayúscula y contener solo mayúsculas, números y guiones bajos.";
            }
            return null;
        },

        placa: function (v) {
            if (!v) return null;
            const limpio = v.replace(/[\s\-]/g, "").toUpperCase();
            if (!RE.placa.test(limpio)) {
                return "La placa no tiene un formato válido.";
            }
            return null;
        },

        coordenada_lat: function (v) {
            if (v === "" || v === null) return null;
            const n = parseFloat(v);
            if (isNaN(n)) return "Debe ser un número.";
            if (n < 0.6 || n > 12.3) return "Latitud fuera de Venezuela (0.6 - 12.3).";
            return null;
        },

        coordenada_lng: function (v) {
            if (v === "" || v === null) return null;
            const n = parseFloat(v);
            if (isNaN(n)) return "Debe ser un número.";
            if (n < -73.4 || n > -59.8) return "Longitud fuera de Venezuela (-73.4 - -59.8).";
            return null;
        },

        entero_positivo: function (v) {
            if (v === "" || v === null) return null;
            const n = parseInt(v, 10);
            if (isNaN(n) || n < 0) return "Debe ser un número entero positivo.";
            if (n > 1000000) return "El valor es demasiado alto.";
            return null;
        },

        fecha_pasada_valida: function (v) {
            // Solo permite fechas desde hoy 00:00 (con grace de 5 min).
            // Rechaza cualquier fecha claramente en el pasado.
            if (!v) return null;
            const fecha = new Date(v);
            if (isNaN(fecha.getTime())) return "Fecha inválida.";

            const ahora = new Date();
            const limite = new Date(ahora.getTime() - 5 * 60 * 1000); // 5 min atrás
            const inicioHoy = new Date();
            inicioHoy.setHours(0, 0, 0, 0);

            if (fecha < inicioHoy && fecha < limite) {
                return "La fecha no puede estar en el pasado. Reporta el incidente con la fecha actual.";
            }
            if (fecha > new Date(ahora.getTime() + 5 * 60 * 1000)) {
                return "La fecha no puede estar en el futuro.";
            }
            return null;
        },

        fecha_futura: function (v) {
            if (!v) return null;
            const fecha = new Date(v);
            if (isNaN(fecha.getTime())) return "Fecha inválida.";
            const ahora = new Date();
            if (fecha < new Date(ahora.getTime() - 5 * 60 * 1000)) {
                return "La fecha no puede estar en el pasado.";
            }
            return null;
        },
    };

    // Aplica validación a un campo
    function validarCampo(input) {
        const tipo = input.dataset.validator;
        if (!tipo || !validadores[tipo]) return null;
        return validadores[tipo](input.value);
    }

    // Muestra/oculta el error en el campo
    function setError(input, mensaje) {
        const wrapper = input.closest(".panel-field") || input.parentElement;
        let errorEl = wrapper.querySelector(".panel-field-error");

        if (mensaje) {
            if (!errorEl) {
                errorEl = document.createElement("div");
                errorEl.className = "panel-field-error";
                errorEl.setAttribute("role", "alert");
                wrapper.appendChild(errorEl);
            }
            errorEl.textContent = mensaje;
            input.classList.add("is-invalid");
            input.setAttribute("aria-invalid", "true");
        } else {
            if (errorEl) errorEl.remove();
            input.classList.remove("is-invalid");
            input.removeAttribute("aria-invalid");
        }
    }

    // Valida todos los campos visibles del form
    function validarFormulario(form) {
        let valido = true;
        form.querySelectorAll("[data-validator]").forEach(function (input) {
            const error = validarCampo(input);
            setError(input, error);
            if (error) valido = false;
        });
        return valido;
    }

    // Bind eventos
    function bindForm(form) {
        form.querySelectorAll("[data-validator]").forEach(function (input) {
            // Validar al perder foco (menos molesto que en cada tecla)
            input.addEventListener("blur", function () {
                setError(input, validarCampo(input));
            });
            // Revalidar en vivo si ya estaba marcado con error
            input.addEventListener("input", function () {
                if (input.classList.contains("is-invalid")) {
                    setError(input, validarCampo(input));
                }
            });
        });

        // Validar antes de enviar
        form.addEventListener("submit", function (e) {
            if (!validarFormulario(form)) {
                e.preventDefault();
                const primerError = form.querySelector(".is-invalid");
                if (primerError) {
                    primerError.focus();
                    primerError.scrollIntoView({ behavior: "smooth", block: "center" });
                }
            }
        });
    }

    // Auto-init: todos los form con data-validate="true"
    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll('form[data-validate="true"]').forEach(bindForm);
    });

    // Exponer para debug
    window.ViaRescateValidators = {
        validarCampo: validarCampo,
        validarFormulario: validarFormulario,
        setError: setError,
    };
})();
