(function (window) {
    "use strict";

    const GIS = (window.ViaRescateGIS = window.ViaRescateGIS || {});

    GIS.createLayers = function (map, definitions) {
        const layers = {};

        Object.keys(definitions).forEach(function (name) {
            layers[name] = L.layerGroup();

            if (definitions[name].visible !== false) {
                layers[name].addTo(map);
            }
        });

        return layers;
    };

    GIS.loadLayer = async function (name, config) {
        const {
            map,
            layer,
            bounds,
            url,
            style,
            markerStyle,
            popup,
            pointToLayer,
        } = config;

        try {
            const response = await fetch(url, {
                headers: {
                    Accept: "application/json",
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();

            if (!data || !Array.isArray(data.features)) {
                throw new Error("Respuesta GeoJSON inválida");
            }

            if (data.features.length === 0) {
                return {
                    name,
                    count: 0,
                };
            }

            GIS.extendBounds(bounds, data);

            const options = {
                onEachFeature(feature, featureLayer) {
                    if (popup) {
                        featureLayer.bindPopup(
                            popup(feature.properties)
                        );
                    }
                },
            };

            if (style) {
                options.style = style;
            }

            if (pointToLayer) {
                options.pointToLayer = pointToLayer;
            } else if (markerStyle) {
                options.pointToLayer = function (feature, latlng) {
                    return L.circleMarker(
                        latlng,
                        markerStyle(name)
                    );
                };
            }

            L.geoJSON(data, options).addTo(layer);

            return {
                name,
                count: data.features.length,
            };
        } catch (error) {
            console.error(
                `No se pudo cargar la capa ${name}:`,
                error
            );

            return {
                name,
                count: 0,
                error: true,
            };
        }
    };

    GIS.toggleLayer = function (map, layer, visible) {
        if (visible) {
            layer.addTo(map);
        } else {
            map.removeLayer(layer);
        }
    };
})(window);
