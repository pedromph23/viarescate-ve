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
})(window);
