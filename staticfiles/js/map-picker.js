/**
 * Map picker — selecciona ubicación con pin arrastrable.
 *
 * Flujo:
 * 1. Si el form tiene coordenadas (edición), inicializa el pin ahí.
 * 2. Al cambiar el <select id_estado>, mueve el pin al centroide del estado.
 * 3. Al arrastrar el pin, actualiza los inputs readonly #id_latitud/#id_longitud.
 */
(function () {
    "use strict";

    function initMapPicker() {
        const mapDiv = document.getElementById("map-picker");
        if (!mapDiv || typeof L === "undefined") return;

        const latInput = document.getElementById("id_latitud");
        const lngInput = document.getElementById("id_longitud");
        const estadoSelect = document.getElementById("id_estado");

        if (!latInput || !lngInput) {
            console.warn("[map-picker] No se encontraron inputs lat/lng");
            return;
        }

        // Leer centroides del JSON embebido
        let centroides = {};
        const scriptTag = document.getElementById("estados-centroides");
        if (scriptTag) {
            try {
                centroides = JSON.parse(scriptTag.textContent);
            } catch (e) {
                console.warn("[map-picker] JSON de centroides inválido", e);
            }
        }

        // Ubicación inicial
        const currentLat = parseFloat(mapDiv.dataset.lat);
        const currentLng = parseFloat(mapDiv.dataset.lng);

        let initialLat, initialLng, initialZoom;
        if (!isNaN(currentLat) && !isNaN(currentLng)) {
            initialLat = currentLat;
            initialLng = currentLng;
            initialZoom = 15;
        } else {
            // Fallback: Caracas
            initialLat = 10.4806;
            initialLng = -66.9036;
            initialZoom = 6;
        }

        // Crear mapa
        const map = L.map(mapDiv, {
            center: [initialLat, initialLng],
            zoom: initialZoom,
            scrollWheelZoom: true,
        });

        // Esri World Street Map: raster gratuito, sin API key, ideal para paneles
        L.tileLayer(
            "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
            {
                attribution: "Tiles © Esri — Source: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri (Thailand), TomTom, 2012",
                maxZoom: 19,
            }
        ).addTo(map);

        // Pin arrastrable
        const marker = L.marker([initialLat, initialLng], {
            draggable: true,
            autoPan: true,
        }).addTo(map);

        // Actualiza inputs al mover pin
        function updateInputs(lat, lng) {
            latInput.value = lat.toFixed(6);
            lngInput.value = lng.toFixed(6);
            // Disparar blur para que validators.js revalide
            latInput.dispatchEvent(new Event("blur", { bubbles: true }));
            lngInput.dispatchEvent(new Event("blur", { bubbles: true }));
        }

        // Inicializar inputs con el valor actual del marcador
        if (isNaN(currentLat) || isNaN(currentLng)) {
            updateInputs(initialLat, initialLng);
        }

        // Drag del pin
        marker.on("dragend", function () {
            const pos = marker.getLatLng();
            updateInputs(pos.lat, pos.lng);
        });

        // Click en el mapa mueve el pin
        map.on("click", function (e) {
            marker.setLatLng(e.latlng);
            updateInputs(e.latlng.lat, e.latlng.lng);
        });

        // Cambio de estado → mover pin al centroide
        if (estadoSelect) {
            estadoSelect.addEventListener("change", function () {
                const estadoId = estadoSelect.value;
                if (!estadoId || !centroides[estadoId]) return;

                const c = centroides[estadoId];
                if (c.lat == null || c.lng == null) return;

                marker.setLatLng([c.lat, c.lng]);
                map.setView([c.lat, c.lng], 8);
                updateInputs(c.lat, c.lng);
            });
        }

        // Forzar recálculo de tamaño (por si el mapa arrancó oculto)
        setTimeout(function () { map.invalidateSize(); }, 100);
    }

    document.addEventListener("DOMContentLoaded", initMapPicker);
})();
