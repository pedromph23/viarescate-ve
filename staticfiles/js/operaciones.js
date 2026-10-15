document.addEventListener("DOMContentLoaded", async () => {
    "use strict";

    const GIS = window.ViaRescateGIS;

    if (!GIS) {
        console.error("ViaRescateGIS no está disponible.");
        return;
    }

    const map = GIS.createMap("operations-map", {
        center: [8, -66],
        zoom: 6,
    });

    if (!map) {
        console.error("No se pudo inicializar el mapa operativo.");
        return;
    }

    const bounds = GIS.createBounds();

    const definitions = {
        centros: {
            map,
            layer: null,
            bounds,
            url: "/mapa/api/geojson/centros-ayuda/",
            markerStyle: GIS.markerStyle,
            popup: function (properties) {
                return GIS.markerPopup(properties, "centros");
            },
        },

        refugios: {
            map,
            layer: null,
            bounds,
            url: "/mapa/api/geojson/refugios/",
            markerStyle: GIS.markerStyle,
            popup: function (properties) {
                return GIS.markerPopup(properties, "refugios");
            },
        },

        vias: {
            map,
            layer: null,
            bounds,
            url: "/mapa/api/geojson/vias/",
            style: GIS.viaStyle,
            popup: GIS.viaPopup,
        },

        reportes: {
            map,
            layer: null,
            bounds,
            url: "/mapa/api/geojson/reportes-viales/",
            markerStyle: GIS.markerStyle,
            popup: GIS.reportPopup,
        },

        vehiculos: {
            map,
            layer: null,
            bounds,
            url: "/mapa/api/geojson/vehiculos/",
            markerStyle: GIS.vehicleStyle,
            popup: GIS.vehiclePopup,
        },

        misiones: {
            map,
            layer: null,
            bounds,
            url: "/mapa/api/geojson/misiones/",
            style: GIS.missionStyle,
            popup: GIS.missionPopup,
            pointToLayer: function (feature, latlng) {
                if (feature.properties?.punto) {
                    return L.circleMarker(
                        latlng,
                        GIS.missionPointStyle(feature)
                    );
                }

                return L.circleMarker(
                    latlng,
                    GIS.missionPointStyle({
                        properties: {
                            punto: "origen",
                        },
                    })
                );
            },
        },
    };

    const layers = GIS.createLayers(map, definitions);

    Object.keys(definitions).forEach(function (name) {
        definitions[name].layer = layers[name];
    });

    let total = 0;
    let errores = 0;

    GIS.setStatus(
        "Cargando información geográfica...",
        "loading"
    );

    const results = await Promise.all(
        Object.entries(definitions).map(
            async ([name, config]) => {
                return GIS.loadLayer(name, config);
            }
        )
    );

    results.forEach(function (result) {
        total += result.count || 0;

        if (result.error) {
            errores += 1;
        }
    });

    GIS.bindLayerControls(map, layers);

    GIS.fitBounds(map, bounds);

    if (errores === 0) {
        GIS.setStatus(
            `${total} elementos geográficos cargados.`,
            "success"
        );
    } else {
        GIS.setStatus(
            `Mapa cargado con ${errores} capa(s) con problemas.`,
            "warning"
        );
    }
});
