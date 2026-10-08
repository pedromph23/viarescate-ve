(function (window) {
    "use strict";

    const GIS = (window.ViaRescateGIS = window.ViaRescateGIS || {});

    GIS.bindLayerControls = function (map, layers) {
        Object.keys(layers).forEach(function (name) {
            const input = document.querySelector(
                `[data-layer-toggle="${name}"]`
            );

            if (!input) {
                return;
            }

            input.addEventListener("change", function (event) {
                GIS.toggleLayer(
                    map,
                    layers[name],
                    event.target.checked
                );
            });
        });
    };
})(window);
