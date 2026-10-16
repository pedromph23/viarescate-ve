(function () {
    "use strict";
    // Confirmación antes de eliminar en formularios con .panel-btn-danger
    document.addEventListener("submit", function (e) {
        const form = e.target;
        const btn = form.querySelector(".panel-btn-danger");
        if (btn && !form.dataset.confirmed) {
            if (!confirm("¿Confirma la eliminación? Esta acción no se puede deshacer.")) {
                e.preventDefault();
            }
        }
    });
})();
