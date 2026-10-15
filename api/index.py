import os
import sys
from pathlib import Path

# Añadir la raíz del proyecto al path de Python
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
