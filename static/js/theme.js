(function () {
    "use strict";
    const STORAGE_KEY = "viarescate-theme";

    function getStored() {
        try { return localStorage.getItem(STORAGE_KEY); }
        catch (e) { return null; }
    }
    function setStored(value) {
        try { localStorage.setItem(STORAGE_KEY, value); } catch (e) {}
    }
    function applyTheme(theme) {
        document.documentElement.setAttribute("data-theme", theme);
    }

    // Aplicar al cargar (el script inline ya lo hizo, pero reforzamos)
    const stored = getStored();
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const initial = stored || (prefersDark ? "dark" : "light");
    applyTheme(initial);

    // Toggle
    document.addEventListener("click", function (e) {
        const btn = e.target.closest("[data-theme-toggle]");
        if (!btn) return;
        const current = document.documentElement.getAttribute("data-theme") || "light";
        const next = current === "dark" ? "light" : "dark";
        applyTheme(next);
        setStored(next);
    });
})();
