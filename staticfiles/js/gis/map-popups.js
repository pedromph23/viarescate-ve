(function (window) {
    "use strict";

    const GIS = (window.ViaRescateGIS = window.ViaRescateGIS || {});

    GIS.layerLabels = {
        centros: "centros de ayuda",
        refugios: "refugios",
        vias: "vías",
        reportes: "incidencias viales",
    };

    GIS.escapeHtml = function (value) {
        const element = document.createElement("div");
        element.textContent = value ?? "";
        return element.innerHTML;
    };

    GIS.markerPopup = function (properties, name) {
        const title =
            properties.nombre ||
            properties.titulo ||
            GIS.layerLabels[name];

        let content = `
            <div class="map-popup">
                <strong>${GIS.escapeHtml(title)}</strong>
        `;

        if (properties.tipo_label || properties.tipo) {
            content += `
                <p>
                    <span class="map-popup-label">Tipo:</span>
                    ${GIS.escapeHtml(
                        properties.tipo_label || properties.tipo || ""
                    )}
                </p>
            `;
        }

        if (properties.estado) {
            content += `
                <p>
                    <span class="map-popup-label">Ubicación:</span>
                    ${GIS.escapeHtml(properties.estado)}
                    ${
                        properties.municipio
                            ? `, ${GIS.escapeHtml(properties.municipio)}`
                            : ""
                    }
                </p>
            `;
        }

        if (properties.parroquia) {
            content += `
                <p>
                    <span class="map-popup-label">Parroquia:</span>
                    ${GIS.escapeHtml(properties.parroquia)}
                </p>
            `;
        }

        if (properties.direccion) {
            content += `
                <p>${GIS.escapeHtml(properties.direccion)}</p>
            `;
        }

        if (properties.telefono) {
            content += `
                <p>
                    <span class="map-popup-label">Teléfono:</span>
                    ${GIS.escapeHtml(properties.telefono)}
                </p>
            `;
        }

        if (properties.capacidad !== undefined) {
            content += `
                <p>
                    <span class="map-popup-label">Capacidad:</span>
                    ${GIS.escapeHtml(String(properties.capacidad))}
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
                    ${GIS.escapeHtml(String(properties.ocupacion))}
                    ${
                        porcentaje !== undefined
                            ? ` (${GIS.escapeHtml(String(porcentaje))}%)`
                            : ""
                    }
                </p>
            `;
        }

        content += "</div>";

        return content;
    };

    GIS.reportPopup = function (properties) {
        return `
            <div class="map-popup">
                <strong>${GIS.escapeHtml(properties.titulo)}</strong>
                <p>
                    <span class="map-popup-label">Tipo:</span>
                    ${GIS.escapeHtml(
                        properties.tipo_label || properties.tipo
                    )}
                </p>
                <p>
                    <span class="map-popup-label">Severidad:</span>
                    ${GIS.escapeHtml(String(properties.severidad))}
                </p>
                <p>${GIS.escapeHtml(properties.descripcion || "")}</p>
                ${
                    properties.via
                        ? `<p>
                            <span class="map-popup-label">Vía:</span>
                            ${GIS.escapeHtml(properties.via)}
                        </p>`
                        : ""
                }
            </div>
        `;
    };

    GIS.viaPopup = function (properties) {
        return `
            <div class="map-popup">
                <strong>${GIS.escapeHtml(properties.nombre)}</strong>
                <p>
                    <span class="map-popup-label">
                        Estado:
                    </span>
                    ${GIS.escapeHtml(
                        properties.estado_vial_label ||
                            properties.estado_vial ||
                            ""
                    )}
                </p>
                ${
                    properties.estado
                        ? `<p>${GIS.escapeHtml(properties.estado)}</p>`
                        : ""
                }
                ${
                    properties.velocidad_referencial
                        ? `<p>
                            <span class="map-popup-label">
                                Velocidad referencial:
                            </span>
                            ${GIS.escapeHtml(
                                String(
                                    properties.velocidad_referencial
                                )
                            )} km/h
                        </p>`
                        : ""
                }
            </div>
        `;
    };

    GIS.vehiclePopup = function (properties) {
        return `
            <div class="map-popup">
                <strong>
                    Vehículo ${GIS.escapeHtml(properties.placa || "")}
                </strong>

                <p>
                    <span class="map-popup-label">Tipo:</span>
                    ${GIS.escapeHtml(properties.tipo || "")}
                </p>

                <p>
                    <span class="map-popup-label">Estado:</span>
                    ${GIS.escapeHtml(
                        properties.estado_operativo_label ||
                        properties.estado_operativo ||
                        ""
                    )}
                </p>

                <p>
                    <span class="map-popup-label">Capacidad:</span>
                    ${GIS.escapeHtml(
                        String(properties.capacidad_kg || "0")
                    )} kg
                </p>

                ${
                    properties.centro
                        ? `<p>
                            <span class="map-popup-label">Centro:</span>
                            ${GIS.escapeHtml(properties.centro)}
                        </p>`
                        : ""
                }

                ${
                    properties.conductor
                        ? `<p>
                            <span class="map-popup-label">Conductor:</span>
                            ${GIS.escapeHtml(properties.conductor)}
                        </p>`
                        : ""
                }

                ${
                    properties.observaciones
                        ? `<p>${GIS.escapeHtml(
                            properties.observaciones
                        )}</p>`
                        : ""
                }
            </div>
        `;
    };

    GIS.missionPopup = function (properties) {
        const point = properties.punto;

        if (point) {
            return `
                <div class="map-popup">
                    <strong>
                        ${GIS.escapeHtml(properties.codigo || "")}
                    </strong>

                    <p>
                        <span class="map-popup-label">Misión:</span>
                        ${GIS.escapeHtml(properties.nombre || "")}
                    </p>

                    <p>
                        <span class="map-popup-label">
                            ${
                                point === "origen"
                                    ? "Origen"
                                    : "Destino"
                            }:
                        </span>
                        ${GIS.escapeHtml(
                            properties.estado_mision_label ||
                            properties.estado_mision ||
                            ""
                        )}
                    </p>
                </div>
            `;
        }

        return `
            <div class="map-popup">
                <strong>
                    ${GIS.escapeHtml(properties.codigo || "")}
                </strong>

                <p>
                    <span class="map-popup-label">Misión:</span>
                    ${GIS.escapeHtml(properties.nombre || "")}
                </p>

                <p>
                    <span class="map-popup-label">Estado:</span>
                    ${GIS.escapeHtml(
                        properties.estado_mision_label ||
                        properties.estado_mision ||
                        ""
                    )}
                </p>

                <p>
                    <span class="map-popup-label">Modo:</span>
                    ${GIS.escapeHtml(
                        properties.modo_ruta_label ||
                        properties.modo_ruta ||
                        ""
                    )}
                </p>

                <p>
                    <span class="map-popup-label">Prioridad:</span>
                    ${GIS.escapeHtml(
                        String(properties.prioridad || "")
                    )}
                </p>

                ${
                    properties.vehiculo
                        ? `<p>
                            <span class="map-popup-label">
                                Vehículo:
                            </span>
                            ${GIS.escapeHtml(properties.vehiculo)}
                        </p>`
                        : ""
                }

                ${
                    properties.coordinador
                        ? `<p>
                            <span class="map-popup-label">
                                Coordinador:
                            </span>
                            ${GIS.escapeHtml(
                                properties.coordinador
                            )}
                        </p>`
                        : ""
                }

                ${
                    properties.distancia_km
                        ? `<p>
                            <span class="map-popup-label">
                                Distancia:
                            </span>
                            ${GIS.escapeHtml(
                                properties.distancia_km
                            )} km
                        </p>`
                        : ""
                }

                ${
                    properties.tiempo_estimado_minutos
                        ? `<p>
                            <span class="map-popup-label">
                                Tiempo estimado:
                            </span>
                            ${GIS.escapeHtml(
                                String(
                                    properties
                                        .tiempo_estimado_minutos
                                )
                            )} min
                        </p>`
                        : ""
                }

                ${
                    properties.descripcion
                        ? `<p>${GIS.escapeHtml(
                            properties.descripcion
                        )}</p>`
                        : ""
                }
            </div>
        `;
    };

})(window);
