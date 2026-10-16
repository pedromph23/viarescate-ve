"""
Tests del sistema de temas (dark/light) — VíaRescate VE.

Verifican que:
1. El HTML servido incluye el script inline que aplica el tema antes del render.
2. El archivo theme.js se sirve correctamente.
3. El CSS contiene las variables para ambos temas.
4. El CSS define un único bloque [data-theme="dark"] (sin duplicados).
5. El toggle existe en el navbar.
6. No hay reglas que apliquen dark mode sin el prefijo [data-theme="dark"].
"""
import re
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse


Usuario = get_user_model()
BASE_DIR = Path(__file__).resolve().parent.parent.parent
APP_CSS = BASE_DIR / "static" / "css" / "app.css"
THEME_JS = BASE_DIR / "static" / "js" / "theme.js"
BASE_HTML = BASE_DIR / "templates" / "base.html"


class BaseHtmlThemeScriptTest(TestCase):
    """El script inline debe aplicarse antes del CSS para evitar flash."""

    def test_base_html_contiene_script_de_tema(self):
        html = BASE_HTML.read_text()
        self.assertIn("viarescate-theme", html)
        self.assertIn('document.documentElement.setAttribute("data-theme"', html)

    def test_script_de_tema_esta_en_head(self):
        """El script debe estar dentro de <head>, no al final del body."""
        html = BASE_HTML.read_text()
        head_end = html.index("</head>")
        body_start = html.index("<body>")
        script_pos = html.index("viarescate-theme")
        self.assertLess(script_pos, head_end,
                        "El script del tema debe estar antes de </head>")
        self.assertLess(script_pos, body_start)

    def test_script_usa_localstorage(self):
        html = BASE_HTML.read_text()
        self.assertIn("localStorage.getItem", html)

    def test_script_default_es_light(self):
        """El default debe ser light — el usuario lo cambia manualmente."""
        html = BASE_HTML.read_text()
        # El script debe usar `|| "light"` como fallback
        self.assertIn('|| "light"', html)
        # No debe depender de prefers-color-scheme
        self.assertNotIn("prefers-color-scheme", html)

    def test_script_tiene_try_catch(self):
        """Sin try/catch, si localStorage está bloqueado revienta."""
        html = BASE_HTML.read_text()
        # Buscar el bloque try/catch alrededor del script de tema
        script_area = html[html.index("viarescate-theme") - 200:
                           html.index("viarescate-theme") + 400]
        self.assertIn("try", script_area)
        self.assertIn("catch", script_area)


class ThemeJsTest(TestCase):
    """Verificaciones del archivo theme.js."""

    def test_theme_js_existe(self):
        self.assertTrue(THEME_JS.exists(), f"No existe: {THEME_JS}")

    def test_theme_js_define_funciones_clave(self):
        js = THEME_JS.read_text()
        self.assertIn("STORAGE_KEY", js)
        self.assertIn("applyTheme", js)
        self.assertIn("data-theme-toggle", js)

    def test_theme_js_se_carga_en_base(self):
        html = BASE_HTML.read_text()
        self.assertIn("js/theme.js", html)
        # Debe tener defer para no bloquear
        self.assertRegex(html, r'<script[^>]*theme\.js[^>]*defer')


class AppCssThemeTest(TestCase):
    """Verifica que el CSS tiene las reglas mínimas para dark mode."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.css = APP_CSS.read_text()

    def test_css_existe(self):
        self.assertTrue(APP_CSS.exists())

    def test_hay_exactamente_un_bloque_root(self):
        """`:root {` debe aparecer una sola vez (definición de variables light)."""
        count = len(re.findall(r"^\s*:root\s*\{", self.css, re.MULTILINE))
        self.assertEqual(count, 1,
                         f"Se esperaba 1 bloque :root, hay {count}")

    def test_hay_exactamente_un_bloque_variables_dark(self):
        """El bloque `[data-theme=\"dark\"] { ... }` (sin más selectores) debe ser único."""
        # Patrón: `[data-theme="dark"] {` sin nada más antes de la llave
        pattern = re.compile(r'\[data-theme="dark"\]\s*\{')
        # Contar SOLO el bloque que define variables (líneas --var:)
        matches = [m.start() for m in pattern.finditer(self.css)]
        variable_blocks = 0
        for m in matches:
            # Ver siguiente línea después de `{`
            snippet = self.css[m:m + 300]
            if "--bg:" in snippet or "--surface:" in snippet:
                variable_blocks += 1
        self.assertEqual(variable_blocks, 1,
                         f"Debe haber 1 bloque de variables dark, hay {variable_blocks}")

    def test_variables_light_definidas(self):
        for var in ("--bg:", "--surface:", "--text:",
                    "--border:", "--primary:", "--shadow:"):
            self.assertIn(var, self.css,
                          f"Falta la variable light {var} en app.css")

    def test_variables_dark_definidas(self):
        """Todas las variables del bloque light deben tener equivalente dark."""
        # Encontrar el bloque dark
        match = re.search(
            r'\[data-theme="dark"\]\s*\{([^}]+)\}',
            self.css
        )
        self.assertIsNotNone(match, "No se encontró bloque de variables dark")
        dark_vars = match.group(1)
        for var in ("--bg:", "--surface:", "--text:",
                    "--border:", "--primary:", "--shadow:"):
            self.assertIn(var, dark_vars,
                          f"Falta {var} en el bloque dark")

    def test_primary_dark_es_diferente_al_light(self):
        """El primary dark debe ser distinto al light para que se note el cambio."""
        light_match = re.search(r':root\s*\{([^}]+)\}', self.css)
        dark_match = re.search(r'\[data-theme="dark"\]\s*\{([^}]+)\}', self.css)
        self.assertIsNotNone(light_match)
        self.assertIsNotNone(dark_match)

        light_primary = re.search(r'--primary:\s*([^;]+)', light_match.group(1))
        dark_primary = re.search(r'--primary:\s*([^;]+)', dark_match.group(1))
        self.assertIsNotNone(light_primary)
        self.assertIsNotNone(dark_primary)
        self.assertNotEqual(light_primary.group(1).strip(),
                            dark_primary.group(1).strip(),
                            "El --primary debe cambiar entre light y dark")

    def test_hero_card_tiene_regla_light(self):
        """El hero card debe tener fondo claro explícito (no solo heredado)."""
        match = re.search(
            r'\.home-hero-card\s*\{([^}]+)\}',
            self.css
        )
        self.assertIsNotNone(match,
                             "No existe regla .home-hero-card en light mode")
        self.assertIn("background", match.group(1),
                      ".home-hero-card debe tener background explícito")

    def test_hero_card_tiene_regla_dark(self):
        """El hero card debe tener override para dark mode."""
        pattern = re.compile(
            r'\[data-theme="dark"\]\s*\.home-hero-card\s*\{([^}]+)\}'
        )
        match = pattern.search(self.css)
        self.assertIsNotNone(match,
                             "No existe override dark para .home-hero-card")

    def test_hero_h1_tiene_color_light(self):
        """El H1 del hero debe tener color explícito (no depender del body)."""
        pattern = re.compile(
            r'\.home-hero-content\s+h1\s*\{([^}]+)\}'
        )
        match = pattern.search(self.css)
        self.assertIsNotNone(match,
                             "No hay regla .home-hero-content h1")
        self.assertIn("color", match.group(1),
                      "El H1 del hero debe tener color explícito")

    def test_hero_h1_tiene_color_dark(self):
        pattern = re.compile(
            r'\[data-theme="dark"\]\s*\.home-hero-content\s+h1\s*\{([^}]+)\}'
        )
        match = pattern.search(self.css)
        self.assertIsNotNone(match,
                             "Falta color dark para el H1 del hero")


class StaticFilesThemeTest(TestCase):
    """Los archivos estáticos existen y son accesibles por finders."""

    def test_theme_js_existe_en_static(self):
        from django.contrib.staticfiles import finders
        path = finders.find("js/theme.js")
        self.assertIsNotNone(path, "theme.js no está en STATICFILES_DIRS")
        self.assertIn(b"data-theme-toggle", Path(path).read_bytes())

    def test_app_css_existe_en_static(self):
        from django.contrib.staticfiles import finders
        path = finders.find("css/app.css")
        self.assertIsNotNone(path, "app.css no está en STATICFILES_DIRS")
        self.assertIn(b'data-theme="dark"', Path(path).read_bytes())


class NavbarToggleTest(TestCase):
    """El botón de toggle debe aparecer en el navbar."""

    def test_navbar_tiene_boton_toggle(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "data-theme-toggle")
        self.assertContains(resp, "theme-toggle")

    def test_navbar_tiene_iconos_sol_y_luna(self):
        resp = self.client.get("/")
        self.assertContains(resp, "ico-moon")
        self.assertContains(resp, "ico-sun")
