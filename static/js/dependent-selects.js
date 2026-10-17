/**
 * Cascading selects: estado → municipio → parroquia.
 *
 * Escucha cambios en #id_estado y #id_municipio, hace fetch a la API y
 * reemplaza las opciones de los selects hijos.
 *
 * Preserva valores iniciales en caso de edición de un registro existente.
 */
(function () {
    "use strict";

    function initDependentSelects() {
        const estadoSelect = document.getElementById("id_estado");
        const municipioSelect = document.getElementById("id_municipio");
        const parroquiaSelect = document.getElementById("id_parroquia");

        if (!estadoSelect || !municipioSelect || !parroquiaSelect) return;

        // Guardar valores actuales (para edición de registro existente)
        const initialMunicipio = municipioSelect.value;
        const initialParroquia = parroquiaSelect.value;

        function setOptions(select, items, placeholder) {
            select.innerHTML = "";
            const placeholderOpt = document.createElement("option");
            placeholderOpt.value = "";
            placeholderOpt.textContent = placeholder;
            select.appendChild(placeholderOpt);

            items.forEach(function (item) {
                const opt = document.createElement("option");
                opt.value = item.id;
                opt.textContent = item.nombre;
                select.appendChild(opt);
            });
        }

        function loadMunicipios(estadoId, preselectId) {
            if (!estadoId) {
                setOptions(municipioSelect, [], "---------");
                setOptions(parroquiaSelect, [], "---------");
                return;
            }

            setOptions(municipioSelect, [], "Cargando...");

            fetch(`/api/municipios/${estadoId}/`, {
                headers: { "Accept": "application/json" },
                credentials: "same-origin",
            })
                .then(function (r) {
                    if (!r.ok) throw new Error("HTTP " + r.status);
                    return r.json();
                })
                .then(function (data) {
                    setOptions(municipioSelect, data.municipios, "---------");
                    if (preselectId) {
                        municipioSelect.value = preselectId;
                        loadParroquias(preselectId, initialParroquia);
                    }
                })
                .catch(function (err) {
                    console.error("[dependent-selects] Error cargando municipios:", err);
                    setOptions(municipioSelect, [], "Error al cargar");
                });
        }

        function loadParroquias(municipioId, preselectId) {
            if (!municipioId) {
                setOptions(parroquiaSelect, [], "---------");
                return;
            }

            setOptions(parroquiaSelect, [], "Cargando...");

            fetch(`/api/parroquias/${municipioId}/`, {
                headers: { "Accept": "application/json" },
                credentials: "same-origin",
            })
                .then(function (r) {
                    if (!r.ok) throw new Error("HTTP " + r.status);
                    return r.json();
                })
                .then(function (data) {
                    setOptions(parroquiaSelect, data.parroquias, "---------");
                    if (preselectId) {
                        parroquiaSelect.value = preselectId;
                    }
                })
                .catch(function (err) {
                    console.error("[dependent-selects] Error cargando parroquias:", err);
                    setOptions(parroquiaSelect, [], "Error al cargar");
                });
        }

        // Listeners
        estadoSelect.addEventListener("change", function () {
            loadMunicipios(estadoSelect.value);
        });

        municipioSelect.addEventListener("change", function () {
            loadParroquias(municipioSelect.value);
        });

        // Carga inicial si hay valores (edición o re-render por error de validación)
        if (estadoSelect.value) {
            const tieneMunicipio = initialMunicipio !== "";
            loadMunicipios(estadoSelect.value, tieneMunicipio ? initialMunicipio : null);
        }
    }

    document.addEventListener("DOMContentLoaded", initDependentSelects);
})();
