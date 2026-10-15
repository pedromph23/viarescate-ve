(function (window) {
    "use strict";

    const GIS = (window.ViaRescateGIS = window.ViaRescateGIS || {});

    GIS.createMap = function (elementId, options) {
        const element = document.getElementById(elementId);

        if (!element || typeof L === "undefined") {
            return null;
        }

        const config = options || {};

        const map = L.map(elementId, {
            zoomControl: true,
            preferCanvas: true,
            scrollWheelZoom: true,
            ...(config.mapOptions || {}),
        }).setView(
            config.center || [8.0, -66.0],
            config.zoom || 6
        );

        L.tileLayer(
            config.tileUrl ||
                "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
            {
                maxZoom: config.maxZoom || 19,
                referrerPolicy: "strict-origin-when-cross-origin",
                attribution:
                    config.attribution ||
                    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
            }
        ).addTo(map);

        return map;
    };

    GIS.createBounds = function () {
        return L.latLngBounds([]);
    };

    GIS.extendBounds = function (bounds, geoJsonData) {
        if (
            !bounds ||
            !geoJsonData ||
            !Array.isArray(geoJsonData.features)
        ) {
            return;
        }

        const geoJsonLayer = L.geoJSON(geoJsonData);

        if (geoJsonLayer.getBounds().isValid()) {
            bounds.extend(geoJsonLayer.getBounds());
        }
    };

    GIS.fitBounds = function (map, bounds, options) {
        if (!map || !bounds || !bounds.isValid()) {
            return;
        }

        map.fitBounds(bounds, {
            padding: [32, 32],
            maxZoom: 13,
            animate: false,
            ...(options || {}),
        });
    };

    GIS.setStatus = function (message, type) {
        const status = document.querySelector("[data-map-status]");

        if (!status) {
            return;
        }

        status.textContent = message;
        status.dataset.status = type || "info";
        status.hidden = false;
    };

    GIS.clearStatus = function () {
        const status = document.querySelector("[data-map-status]");

        if (status) {
            status.hidden = true;
        }
    };
})(window);
