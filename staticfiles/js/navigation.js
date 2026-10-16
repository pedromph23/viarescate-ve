(function () {
    "use strict";

    var burger = document.querySelector("[data-nav-burger]");
    var navLinks = document.querySelector("[data-nav-links]");

    if (!burger || !navLinks) return;

    function closeMenu() {
        navLinks.classList.remove("is-open");
        burger.classList.remove("is-open");
        burger.setAttribute("aria-expanded", "false");
        document.body.classList.remove("nav-open");
    }

    function openMenu() {
        navLinks.classList.add("is-open");
        burger.classList.add("is-open");
        burger.setAttribute("aria-expanded", "true");
        document.body.classList.add("nav-open");
    }

    // Toggle del menú
    burger.addEventListener("click", function (e) {
        e.stopPropagation();
        if (navLinks.classList.contains("is-open")) {
            closeMenu();
        } else {
            openMenu();
        }
    });

    // Cerrar al pulsar un enlace
    navLinks.querySelectorAll("a").forEach(function (link) {
        link.addEventListener("click", closeMenu);
    });

    // Cerrar al pulsar fuera del menú
    document.addEventListener("click", function (e) {
        if (!navLinks.classList.contains("is-open")) return;
        if (navLinks.contains(e.target) || burger.contains(e.target)) return;
        closeMenu();
    });

    // Cerrar con Escape
    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && navLinks.classList.contains("is-open")) {
            closeMenu();
        }
    });
})();
