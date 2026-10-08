(function () {
    "use strict";

    const mapElement = document.getElementById("map");

    if (!mapElement || typeof L === "undefined") {
        return;
    }

    const map = L.map("map", {
        zoomControl: true,
        preferCanvas: true,
        scrollWheelZoom: true,
    }).setView([8.0, -66.0], 6);

    L.tileLayer(
        "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
            maxZoom: 19,
            referrerPolicy: "strict-origin-when-cross-origin",
            attribution:
                '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        }
    ).addTo(map);

    const layers = {
        centros: L.layerGroup().addTo(map),
        refugios: L.layerGroup().addTo(map),
        vias: L.layerGroup().addTo(map),
        reportes: L.layerGroup().addTo(map),
    };

    const urls = {
        centros: "/mapa/api/geojson/centros-ayuda/",
        refugios: "/mapa/api/geojson/refugios/",
        vias: "/mapa/api/geojson/vias/",
        reportes: "/mapa/api/geojson/reportes-viales/",
    };

    const layerLabels = {
        centros: "centros de ayuda",
        refugios: "refugios",
        vias: "vías",
        reportes: "incidencias viales",
    };

    const statusColors = {
        NORMAL: "#4f8a68",
        PRECAUCION: "#d49a32",
        AFECTADA: "#df713d",
        CRITICA: "#b84a4a",
        CERRADA: "#555555",
    };

    const markerColors = {
        centros: "#477a66",
        refugios: "#8a6d45",
        reportes: "#b65c58",
    };

    function escapeHtml(value) {
        const element = document.createElement("div");
        element.textContent = value ?? "";
        return element.innerHTML;
    }

    function setMapStatus(message, type) {
        const status = document.querySelector("[data-map-status]");

        if (!status) {
            return;
        }

        status.textContent = message;
        status.dataset.status = type || "info";
        status.hidden = false;
    }

    function clearMapStatus() {
        const status = document.querySelector("[data-map-status]");

        if (status) {
            status.hidden = true;
        }
    }

    function markerStyle(name) {
        return {
            radius: name === "reportes" ? 8 : 9,
            color: "#ffffff",
            weight: 2,
            fillColor: markerColors[name],
            fillOpacity: 0.9,
        };
    }

    function markerPopup(properties, name) {
        const title =
            properties.nombre ||
            properties.titulo ||
            layerLabels[name];

        let content = `
            <div class="map-popup">
                <strong>${escapeHtml(title)}</strong>
        `;

        if (properties.tipo_label || properties.tipo) {
            content += `
                <p>
                    <span class="map-popup-label">Tipo:</span>
                    ${escapeHtml(
                        properties.tipo_label || properties.tipo || ""
                    )}
                </p>
            `;
        }

        if (properties.estado) {
            content += `
                <p>
                    <span class="map-popup-label">Ubicación:</span>
                    ${escapeHtml(properties.estado)}
                    ${
                        properties.municipio
                            ? `, ${escapeHtml(properties.municipio)}`
                            : ""
                    }
                </p>
            `;
        }

        if (properties.parroquia) {
            content += `
                <p>
                    <span class="map-popup-label">Parroquia:</span>
                    ${escapeHtml(properties.parroquia)}
                </p>
            `;
        }

        if (properties.direccion) {
            content += `
                <p>${escapeHtml(properties.direccion)}</p>
            `;
        }

        if (properties.telefono) {
            content += `
                <p>
                    <span class="map-popup-label">Teléfono:</span>
                    ${escapeHtml(properties.telefono)}
                </p>
            `;
        }

        if (properties.capacidad !== undefined) {
            content += `
                <p>
                    <span class="map-popup-label">Capacidad:</span>
                    ${escapeHtml(String(properties.capacidad))}
                </p>
            `;
        }

        if (name === "refugios" && properties.ocupacion !== undefined) {
            const porcentaje =
                properties.porcentaje_ocupacion ??
                properties.ocupacion_porcentaje;

            content += `
                <p>
                    <span class="map-popup-label">Ocupación:</span>
                    ${escapeHtml(String(properties.ocupacion))}
                    ${
                        porcentaje !== undefined
                            ? ` (${escapeHtml(String(porcentaje))}%)`
                            : ""
                    }
                </p>
            `;
        }

        content += "</div>";

        return content;
    }

    function reportPopup(properties) {
        return `
            <div class="map-popup">
                <strong>${escapeHtml(properties.titulo)}</strong>
                <p>
                    <span class="map-popup-label">Tipo:</span>
                    ${escapeHtml(
                        properties.tipo_label || properties.tipo
                    )}
                </p>
                <p>
                    <span class="map-popup-label">Severidad:</span>
                    ${escapeHtml(String(properties.severidad))}
                </p>
                <p>${escapeHtml(properties.descripcion || "")}</p>
                ${
                    properties.via
                        ? `<p>
                            <span class="map-popup-label">Vía:</span>
                            ${escapeHtml(properties.via)}
                        </p>`
                        : ""
                }
            </div>
        `;
    }

    function viaStyle(feature) {
        const estado = feature.properties.estado_vial;

        const styles = {
            NORMAL: {
                color: statusColors.NORMAL,
                weight: 4,
                opacity: 0.85,
            },
            PRECAUCION: {
                color: statusColors.PRECAUCION,
                weight: 5,
                opacity: 0.9,
                dashArray: "8 6",
            },
            AFECTADA: {
                color: statusColors.AFECTADA,
                weight: 5,
                opacity: 0.95,
                dashArray: "10 5",
            },
            CRITICA: {
                color: statusColors.CRITICA,
                weight: 6,
                opacity: 1,
                dashArray: "4 5",
            },
            CERRADA: {
                color: statusColors.CERRADA,
                weight: 7,
                opacity: 1,
                dashArray: "12 8",
            },
        };

        return styles[estado] || styles.NORMAL;
    }

    function extendMapBounds(geoJsonData) {
        if (!geoJsonData || !Array.isArray(geoJsonData.features)) {
            return;
        }

        const geoJsonLayer = L.geoJSON(geoJsonData);

        if (geoJsonLayer.getBounds().isValid()) {
            mapBounds.extend(geoJsonLayer.getBounds());
        }
    }

    async function loadLayer(name) {
        try {
            const response = await fetch(urls[name], {
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

            extendMapBounds(data);

            if (name === "vias") {
                L.geoJSON(data, {
                    style: viaStyle,
                    onEachFeature(feature, layer) {
                        const properties = feature.properties;

                        layer.bindPopup(`
                            <div class="map-popup">
                                <strong>${escapeHtml(
                                    properties.nombre
                                )}</strong>
                                <p>
                                    <span class="map-popup-label">
                                        Estado:
                                    </span>
                                    ${escapeHtml(
                                        properties.estado_vial_label ||
                                            properties.estado_vial ||
                                            ""
                                    )}
                                </p>
                                ${
                                    properties.estado
                                        ? `<p>${escapeHtml(
                                              properties.estado
                                          )}</p>`
                                        : ""
                                }
                                ${
                                    properties.velocidad_referencial
                                        ? `<p>
                                            <span class="map-popup-label">
                                                Velocidad referencial:
                                            </span>
                                            ${escapeHtml(
                                                String(
                                                    properties.velocidad_referencial
                                                )
                                            )} km/h
                                        </p>`
                                        : ""
                                }
                            </div>
                        `);
                    },
                }).addTo(layers.vias);

                return {
                    name,
                    count: data.features.length,
                };
            }

            L.geoJSON(data, {
                pointToLayer(feature, latlng) {
                    return L.circleMarker(
                        latlng,
                        markerStyle(name)
                    );
                },
                onEachFeature(feature, layer) {
                    if (name === "reportes") {
                        layer.bindPopup(
                            reportPopup(feature.properties)
                        );
                    } else {
                        layer.bindPopup(
                            markerPopup(feature.properties, name)
                        );
                    }
                },
            }).addTo(layers[name]);

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
    }

    const mapBounds = L.latLngBounds([]);

    async function initializeLayers() {
        setMapStatus(
            "Cargando información geográfica…",
            "loading"
        );

        const results = await Promise.all(
            Object.keys(layers).map(loadLayer)
        );

        const errors = results.filter(
            (result) => result.error
        );

        const totalFeatures = results.reduce(
            (total, result) => total + result.count,
            0
        );

        if (errors.length > 0) {
            setMapStatus(
                "Algunas capas no pudieron cargarse. Puedes continuar explorando las disponibles.",
                "error"
            );
        } else if (totalFeatures === 0) {
            setMapStatus(
                "No hay información operacional registrada para mostrar en el mapa.",
                "empty"
            );
        } else {
            clearMapStatus();
        }

        if (mapBounds.isValid()) {
            map.fitBounds(mapBounds, {
                padding: [32, 32],
                maxZoom: 13,
                animate: false,
            });
        }
    }

    Object.keys(layers).forEach((name) => {
        const input = document.querySelector(
            `[data-layer-toggle="${name}"]`
        );

        if (!input) {
            return;
        }

        input.addEventListener("change", (event) => {
            if (event.target.checked) {
                layers[name].addTo(map);
            } else {
                map.removeLayer(layers[name]);
            }
        });
    });

    initializeLayers();
})();
