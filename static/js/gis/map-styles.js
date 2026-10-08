(function (window) {
    "use strict";

    const GIS = (window.ViaRescateGIS = window.ViaRescateGIS || {});

    GIS.statusColors = {
        NORMAL: "#4f8a68",
        PRECAUCION: "#d49a32",
        AFECTADA: "#df713d",
        CRITICA: "#b84a4a",
        CERRADA: "#555555",
    };

    GIS.markerColors = {
        centros: "#477a66",
        refugios: "#8a6d45",
        reportes: "#b65c58",
    };

    GIS.markerStyle = function (name) {
        return {
            radius: name === "reportes" ? 8 : 9,
            color: "#ffffff",
            weight: 2,
            fillColor: GIS.markerColors[name],
            fillOpacity: 0.9,
        };
    };

    GIS.viaStyle = function (feature) {
        const estado = feature.properties.estado_vial;

        const styles = {
            NORMAL: {
                color: GIS.statusColors.NORMAL,
                weight: 4,
                opacity: 0.85,
            },
            PRECAUCION: {
                color: GIS.statusColors.PRECAUCION,
                weight: 5,
                opacity: 0.9,
                dashArray: "8 6",
            },
            AFECTADA: {
                color: GIS.statusColors.AFECTADA,
                weight: 5,
                opacity: 0.95,
                dashArray: "10 5",
            },
            CRITICA: {
                color: GIS.statusColors.CRITICA,
                weight: 6,
                opacity: 1,
                dashArray: "4 5",
            },
            CERRADA: {
                color: GIS.statusColors.CERRADA,
                weight: 7,
                opacity: 1,
                dashArray: "12 8",
            },
        };

        return styles[estado] || styles.NORMAL;
    };

    GIS.operationalColors = {
        vehiculos: "#486581",
        origen: "#6b8e71",
        destino: "#a05a5a",
        mision: "#7057a3",
    };

    GIS.vehicleStyle = function () {
        return {
            radius: 8,
            color: "#ffffff",
            weight: 2,
            fillColor: GIS.operationalColors.vehiculos,
            fillOpacity: 0.95,
        };
    };

    GIS.missionStyle = function (feature) {
        const priority = Number(
            feature.properties && feature.properties.prioridad
        );

        const weights = {
            1: 3,
            2: 4,
            3: 5,
            4: 6,
            5: 7,
        };

        return {
            color: GIS.operationalColors.mision,
            weight: weights[priority] || 4,
            opacity: 0.9,
            dashArray: "10 6",
        };
    };

    GIS.missionPointStyle = function (feature) {
        const point = feature.properties && feature.properties.punto;

        return {
            radius: point === "destino" ? 8 : 7,
            color: "#ffffff",
            weight: 2,
            fillColor:
                point === "destino"
                    ? GIS.operationalColors.destino
                    : GIS.operationalColors.origen,
            fillOpacity: 0.95,
        };
    };

})(window);
