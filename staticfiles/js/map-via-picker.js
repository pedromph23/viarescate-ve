/**
 * Editor de LineString para Vías.
 * Click en el mapa agrega puntos. Botones: deshacer, reiniciar.
 * Mantiene el valor del input oculto #id_puntos_json actualizado.
 */
(function () {
    "use strict";

    function initViaMapPicker() {
        const mapDiv = document.getElementById("via-map-picker");
        if (!mapDiv || typeof L === "undefined") return;

        const puntosInput = document.getElementById("id_puntos_json");
        const undoBtn = document.getElementById("via-undo");
        const resetBtn = document.getElementById("via-reset");
        const countBadge = document.getElementById("via-puntos-count");

        if (!puntosInput) return;

        // Cargar puntos iniciales (edición)
        let puntos = [];
        try {
            puntos = JSON.parse(puntosInput.value || "[]");
            if (!Array.isArray(puntos)) puntos = [];
        } catch (e) {
            puntos = [];
        }

        // Centro inicial: primer punto o Caracas
        let center = [10.4806, -66.9036];
        let zoom = 6;
        if (puntos.length > 0) {
            center = [puntos[0].lat, puntos[0].lng];
            zoom = 14;
        }

        const map = L.map(mapDiv, { center: center, zoom: zoom });

        // Esri World Street Map (consistente con map-picker.js)
        L.tileLayer(
            "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
            {
                attribution: "Tiles © Esri",
                maxZoom: 19,
            }
        ).addTo(map);

        // Capa donde dibujamos la línea
        const polyline = L.polyline([], {
            color: "#58a6ff",
            weight: 4,
            opacity: 0.8,
        }).addTo(map);

        // Marcadores de los puntos
        const markersGroup = L.layerGroup().addTo(map);

        function redibujar() {
            polyline.setLatLngs(puntos.map(function (p) { return [p.lat, p.lng]; }));
            markersGroup.clearLayers();

            puntos.forEach(function (p, idx) {
                L.circleMarker([p.lat, p.lng], {
                    radius: 6,
                    color: "#58a6ff",
                    fillColor: "#ffffff",
                    fillOpacity: 1,
                    weight: 2,
                })
                    .bindTooltip(String(idx + 1), { permanent: false })
                    .addTo(markersGroup);
            });

            if (countBadge) {
                countBadge.textContent = puntos.length + " punto" + (puntos.length === 1 ? "" : "s");
            }
            puntosInput.value = JSON.stringify(puntos);
        }

        // Click agrega punto
        map.on("click", function (e) {
            puntos.push({ lat: e.latlng.lat, lng: e.latlng.lng });
            redibujar();
        });

        // Deshacer
        if (undoBtn) {
            undoBtn.addEventListener("click", function () {
                if (puntos.length === 0) return;
                puntos.pop();
                redibujar();
            });
        }

        // Reiniciar
        if (resetBtn) {
            resetBtn.addEventListener("click", function () {
                if (puntos.length === 0) return;
                if (!confirm("¿Eliminar todos los puntos del trazado?")) return;
                puntos = [];
                redibujar();
            });
        }

        redibujar();
        setTimeout(function () { map.invalidateSize(); }, 100);
    }

    document.addEventListener("DOMContentLoaded", initViaMapPicker);
})();
