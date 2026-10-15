import os
import sys
import glob
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# ---------------------------------------------------------------------------
# Precarga de librerías GIS del runtime vercel-python-gis
# ---------------------------------------------------------------------------
# El runtime empaqueta libgdal.so, libgeos_c.so.1, libproj.so.22, etc.
# Pero si no están en LD_LIBRARY_PATH, ctypes no las encuentra.
# Las buscamos y forzamos rutas absolutas.
_gis_dir = None
for _pattern in (
    "/var/task/**/libgdal.so",
    "/var/task/**/dist/files/libgdal.so",
    "/tmp/**/libgdal.so",
):
    _matches = glob.glob(_pattern, recursive=True)
    if _matches:
        _gis_dir = os.path.dirname(_matches[0])
        break

if _gis_dir:
    print(f"[viarescate] GIS libs encontradas en: {_gis_dir}", file=sys.stderr)
    os.environ["GDAL_LIBRARY_PATH"] = os.path.join(_gis_dir, "libgdal.so")
    os.environ["GEOS_LIBRARY_PATH"] = os.path.join(_gis_dir, "libgeos_c.so.1")
    os.environ["PROJ_LIBRARY_PATH"] = os.path.join(_gis_dir, "libproj.so.22")
    os.environ["LD_LIBRARY_PATH"] = _gis_dir + ":" + os.environ.get("LD_LIBRARY_PATH", "")
else:
    print("[viarescate] ADVERTENCIA: no se encontraron las libs GIS", file=sys.stderr)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
