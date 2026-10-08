(function (window) {
    "use strict";

    const GIS = window.ViaRescateGIS;

    if (!GIS || typeof L === "undefined") {
        return;
    }

    const mapElement = document.getElementById("map");

    if (!mapElement) {
        return;
    }

    const map = GIS.createMap("map", {
        center: [8.0, -66.0],
        zoom: 6,
    });

    if (!map) {
        return;
    }

    const definitions = {
        centros: {
            url: "/mapa/api/geojson/centros-ayuda/",
        },
        refugios: {
            url: "/mapa/api/geojson/refugios/",
        },
        vias: {
            url: "/mapa/api/geojson/vias/",
        },
        reportes: {
            url: "/mapa/api/geojson/reportes-viales/",
        },
    };

    const layers = GIS.createLayers(map, definitions);
    const mapBounds = GIS.createBounds();

    async function initializeLayers() {
        GIS.setStatus(
            "Cargando información geográfica…",
            "loading"
        );

        const results = await Promise.all([
            GIS.loadLayer("centros", {
                map,
                layer: layers.centros,
                bounds: mapBounds,
                url: definitions.centros.url,
                markerStyle: GIS.markerStyle,
                popup: function (properties) {
                    return GIS.markerPopup(properties, "centros");
                },
            }),

            GIS.loadLayer("refugios", {
                map,
                layer: layers.refugios,
                bounds: mapBounds,
                url: definitions.refugios.url,
                markerStyle: GIS.markerStyle,
                popup: function (properties) {
                    return GIS.markerPopup(properties, "refugios");
                },
            }),

            GIS.loadLayer("vias", {
                map,
                layer: layers.vias,
                bounds: mapBounds,
                url: definitions.vias.url,
                style: GIS.viaStyle,
                popup: GIS.viaPopup,
            }),

            GIS.loadLayer("reportes", {
                map,
                layer: layers.reportes,
                bounds: mapBounds,
                url: definitions.reportes.url,
                markerStyle: GIS.markerStyle,
                popup: GIS.reportPopup,
            }),
        ]);

        const errors = results.filter(function (result) {
            return result.error;
        });

        const totalFeatures = results.reduce(function (
            total,
            result
        ) {
            return total + result.count;
        }, 0);

        if (errors.length > 0) {
            GIS.setStatus(
                "Algunas capas no pudieron cargarse. Puedes continuar explorando las disponibles.",
                "error"
            );
        } else if (totalFeatures === 0) {
            GIS.setStatus(
                "No hay información operacional registrada para mostrar en el mapa.",
                "empty"
            );
        } else {
            GIS.clearStatus();
        }

        GIS.fitBounds(map, mapBounds);
    }

    GIS.bindLayerControls(map, layers);

    initializeLayers();
})(window);
