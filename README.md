# VíaRescate VE

**Sistema Inteligente de Rutas para Distribución de Ayuda Humanitaria en Venezuela**

Optimización de rutas desde centros de acopio hacia refugios, considerando
distancia, tiempo, estado de las vías, incidentes y prioridad humanitaria.

🌐 **Producción:** https://viarescate-ve.vercel.app

---

## Tabla de contenidos

1. [Características](#características)
2. [Stack tecnológico](#stack-tecnológico)
3. [Arquitectura](#arquitectura)
4. [Instalación local](#instalación-local)
5. [Variables de entorno](#variables-de-entorno)
6. [Tests](#tests)
7. [Despliegue a producción](#despliegue-a-producción)
8. [Problemas resueltos](#problemas-resueltos)
9. [Limitaciones conocidas](#limitaciones-conocidas)
10. [Estructura del proyecto](#estructura-del-proyecto)
11. [Contribuir](#contribuir)

---

## Características

- 🗺️ Mapa interactivo con Leaflet (centros, refugios, vías, reportes, vehículos)
- 🛣️ Motor de optimización de rutas configurable (distancia, tiempo, riesgo, prioridad)
- 📍 PostGIS para consultas geoespaciales (SRID 4326, índices GiST)
- 🚨 Reportes ciudadanos de incidentes viales con evidencia fotográfica
- 📦 Inventario y distribución de ayuda humanitaria por centro de acopio
- 🚚 Gestión de vehículos, misiones y seguimiento en ruta
- 🔐 Autenticación con roles (administrador, coordinador, operador, voluntario, usuario)
- 📊 Dashboard operativo con KPIs y alertas
- 🌓 Modo claro / oscuro, mobile-first, responsive (320px → 1920px)
- 🔄 Recalculo automático de rutas ante cambios en el estado de las vías
- 📝 Auditoría completa de acciones sobre datos sensibles

---

## Stack tecnológico

### Backend

| Componente | Versión |
|-----------|---------|
| Python | 3.12 (producción) / 3.14 (local) |
| Django | 6.1.1 |
| Django REST Framework | 3.18.3 |
| GeoDjango | incluido en Django |
| PostgreSQL | 16 |
| PostGIS | 3.3 |
| WhiteNoise | 6.8.2 |
| Channels + Redis | 4.3.2 / 4.3.0 |
| Celery | 5.6.3 |

### Frontend

- HTML5, CSS3, JavaScript ES6+
- Leaflet (mapas interactivos)
- Tailwind CSS (utilidades)

### Infraestructura

| Entorno | Plataforma |
|---------|-----------|
| Desarrollo | Windows 11 + WSL2 (Ubuntu) + VS Code |
| Repositorio | GitHub |
| Base de datos producción | Supabase (PostgreSQL + PostGIS administrado) |
| Deploy backend | Vercel (runtime Python GIS serverless) |

---

## Arquitectura
┌──────────────────┐
│ USUARIO │
│ PC / TABLET / 📱 │
└────────┬─────────┘
│
▼
┌──────────────────────┐
│ VERCEL │
│ Django WSGI │
│ Serverless Function │
│ + WhiteNoise │
│ + Runtime GIS │
└──────────┬───────────┘
│
▼
┌──────────────────────┐
│ SUPABASE │
│ PostgreSQL + PostGIS │
└──────────────────────┘


### Apps Django

| App | Responsabilidad |
|-----|-----------------|
| `core` | Estados, municipios, parroquias, validadores centrales |
| `usuarios` | Autenticación, roles, permisos |
| `mapa` | Vistas y API del mapa interactivo |
| `operaciones` | Centros, refugios, vías, vehículos, misiones, inventario, reportes |

---

## Instalación local

### Requisitos previos

```bash
python3 --version    # >= 3.12
psql --version       # >= 15
git --version
code --version       # VS Code con extensión WSL

1. Clonar el repositorio

git clone git@github.com:pedromph23/viarescate-ve.git
cd viarescate-ve

2. Crear entorno virtual
bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
3. Configurar PostgreSQL + PostGIS local
bash
sudo apt update
sudo apt install -y postgresql postgresql-16-postgis-3 gdal-bin libgdal-dev

sudo -u postgres psql << 'SQL'
CREATE DATABASE viarescate_ve;
CREATE USER viarescate WITH PASSWORD 'cambia-esto';
GRANT ALL PRIVILEGES ON DATABASE viarescate_ve TO viarescate;
\c viarescate_ve
CREATE EXTENSION IF NOT EXISTS postgis;
SQL
4. Configurar .env
bash
cp .env.example .env
# Editar .env con valores reales
5. Migrar base de datos
bash
python manage.py migrate
python manage.py createsuperuser
6. Levantar servidor
bash
python manage.py runserver 8000
Abrir http://127.0.0.1:8000/

Variables de entorno
Ver .env.example para la plantilla completa. Variables clave:

Desarrollo local (PostgreSQL local)
env
DJANGO_SECRET_KEY=token-de-64-caracteres
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000

DB_NAME=viarescate_ve
DB_USER=viarescate
DB_PASSWORD=cambia-esto
DB_HOST=127.0.0.1
DB_PORT=5432

REDIS_URL=redis://127.0.0.1:6379/0

TIME_ZONE=America/Caracas
LANGUAGE_CODE=es-ve
Producción (Supabase + Vercel)
env
DJANGO_SETTINGS_MODULE=config.settings.production
DJANGO_SECRET_KEY=<token de 64+ chars generado con secrets.token_urlsafe>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=viarescate-ve.vercel.app,.vercel.app
DJANGO_CSRF_TRUSTED_ORIGINS=https://viarescate-ve.vercel.app,https://*.vercel.app
DJANGO_SECURE_SSL_REDIRECT=False

DATABASE_URL=postgis://postgres.<ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres?sslmode=require

USE_S3_MEDIA=False
PIP_BREAK_SYSTEM_PACKAGES=1
Tests
bash
python manage.py check
python manage.py test
Despliegue a producción
Esta sección documenta la configuración crítica para desplegar Django + GeoDjango
en Vercel. Vercel no incluye GDAL/GEOS/PROJ en su runtime estándar, por lo
que se requiere un runtime especializado.

Arquitectura de producción
Componente	Plataforma	Detalle
Backend Django	Vercel	Runtime vercel-python-gis-modern@1.0.6
Base de datos	Supabase	PostgreSQL + PostGIS, pooler :5432
Static files	WhiteNoise	CompressedStaticFilesStorage, staticfiles/ commiteado
Media files	(pendiente)	Supabase Storage S3
1. Supabase — base de datos
Crear proyecto en https://supabase.com

Habilitar PostGIS en SQL Editor → New query:

sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
Verificar:

sql
SELECT postgis_version();
-- Debe devolver: 3.3 USE_GEOS=1 USE_PROJ=1 USE_STATS=1
Obtener la URL de conexión en Settings → Database → Connection string → URI

Formato final de DATABASE_URL (importante el scheme postgis://):

text
postgis://postgres.<ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres?sslmode=require
⚠️ Cambiar postgresql:// por postgis://. Sin ese cambio, Django usa el
backend estándar y PostGIS falla al hacer consultas geoespaciales.

2. Archivos críticos de Vercel
vercel.json
json
{
  "builds": [
    {
      "src": "api/index.py",
      "use": "vercel-python-gis-modern@1.0.6"
    }
  ],
  "rewrites": [
    { "source": "/static", "destination": "/static" },
    { "source": "/(.*)", "destination": "api/index.py" }
  ]
}
api/index.py — punto de entrada
python
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
config/settings/production.py — fragmentos clave
python
import os

DEBUG = False
SECRET_KEY = env("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])

# WhiteNoise — SIN manifest para evitar fallos si falta algún archivo
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"
    },
}

# Rutas GIS — leídas del entorno (el runtime las expone en /var/task/lib)
GDAL_LIBRARY_PATH = os.environ.get("GDAL_LIBRARY_PATH", "libgdal.so")
GEOS_LIBRARY_PATH = os.environ.get("GEOS_LIBRARY_PATH", "libgeos_c.so.1")
PROJ_LIBRARY_PATH = os.environ.get("PROJ_LIBRARY_PATH", "libproj.so")

# Channels in-memory (Vercel no ejecuta Redis persistente)
CHANNEL_LAYERS = {
    "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}
}
3. Configuración en el dashboard de Vercel
Settings → Build & Development:

Campo	Valor
Framework Preset	Other
Build Command	(vacío)
Install Command	(vacío)
Output Directory	(vacío)
Node.js Version	22.x
⚠️ Build Command debe estar VACÍO. El entorno de build de Vercel no
tiene GDAL, por lo que ejecutar python manage.py collectstatic falla con
libgdal.so not found. Los estáticos se generan localmente y se commitean.

Settings → Environment Variables:

Variable	Valor
DJANGO_SETTINGS_MODULE	config.settings.production
DJANGO_SECRET_KEY	(token de 64+ chars)
DJANGO_DEBUG	False
DJANGO_ALLOWED_HOSTS	viarescate-ve.vercel.app,.vercel.app
DJANGO_CSRF_TRUSTED_ORIGINS	https://viarescate-ve.vercel.app,https://*.vercel.app
DJANGO_SECURE_SSL_REDIRECT	False
DATABASE_URL	postgis://... (ver arriba)
USE_S3_MEDIA	False
PIP_BREAK_SYSTEM_PACKAGES	1
PIP_BREAK_SYSTEM_PACKAGES=1 es obligatorio — Vercel usa uv y bloquea
instalaciones globales con pip por PEP 668.

.vercel.app (con punto inicial) permite que los preview deployments
funcionen sin DisallowedHost.

4. Estáticos en el repositorio
Los archivos estáticos se generan en local y se commitean:

bash
# .gitignore NO debe contener staticfiles/
set -a; source .env; set +a
export DJANGO_SETTINGS_MODULE=config.settings.production
export DJANGO_SECURE_SSL_REDIRECT=False

rm -rf staticfiles/
python manage.py collectstatic --noinput
# → ~180 archivos copiados, ~166 post-processed
Luego:

bash
git add staticfiles/
git commit -m "chore: update staticfiles"
git push origin main
5. Migraciones en producción
Desde local, apuntando a Supabase:

bash
set -a; source .env; set +a
export DJANGO_SETTINGS_MODULE=config.settings.production

python manage.py migrate
python manage.py createsuperuser
No ejecutar migraciones desde Vercel. Hacerlo siempre desde local.

6. Proceso completo de deploy
bash
# 1. Cambios en código
git add .
git commit -m "feat: ..."

# 2. Si tocaste CSS/JS/assets, regenerar estáticos
set -a; source .env; set +a
export DJANGO_SETTINGS_MODULE=config.settings.production DJANGO_SECURE_SSL_REDIRECT=False
python manage.py collectstatic --noinput
git add staticfiles/
git commit -m "chore: update staticfiles"

# 3. Push
git push origin main

# 4. Vercel despliega automáticamente (~1-2 min)
7. Verificación post-deploy
bash
curl -I https://viarescate-ve.vercel.app/            # → 200
curl -I https://viarescate-ve.vercel.app/admin/      # → 302 → /admin/login/
curl -I https://viarescate-ve.vercel.app/static/css/app.css  # → 200
Problemas resueltos
Estos son los 5 obstáculos encontrados durante el setup inicial. Documentados
para no repetirlos si se reconfigura el proyecto.

#	Error	Causa	Solución
1	Could not find the GDAL library	Vercel @vercel/python no trae GDAL/GEOS/PROJ	Usar runtime vercel-python-gis-modern@1.0.6
2	spawn pip3.9 ENOENT	vercel-python-gis@1.0.0 espera Python 3.9 (ya no existe en Vercel)	Migrar a vercel-python-gis-modern@1.0.6 (Python 3.12)
3	externally-managed-environment (PEP 668)	Vercel usa uv, bloquea pip install global	Env var PIP_BREAK_SYSTEM_PACKAGES=1
4	Missing staticfiles manifest entry	CompressedManifestStaticFilesStorage exige manifest completo	Cambiar a CompressedStaticFilesStorage
5	libgdal.so not found durante build	collectstatic corre en el build env, que no tiene GDAL	Build Command vacío + staticfiles/ commiteado
Limitaciones conocidas
En Vercel (runtime serverless)
❌ WebSockets persistentes — Vercel no los soporta. Usar Server-Sent Events (SSE)
o polling controlado.

❌ Celery / workers persistentes — no se ejecutan en Vercel. Mover a Railway,
Fly.io o cron externo si se necesitan.

❌ Redis persistente — no disponible en Vercel. CHANNEL_LAYERS usa
InMemoryChannelLayer (válido para dev y baja concurrencia).

⚠️ Media files efímeros — el filesystem de Vercel se resetea en cada deploy.
Activar USE_S3_MEDIA=True con Supabase Storage para persistir.

⚠️ Cold starts — primera request tras inactividad puede tardar 2-5s.

⚠️ Timeout de funciones — Plan Hobby: 10s, Plan Pro: 60s.

Backend
No confiar en el filesystem efímero para datos persistentes.

No usar DEBUG=True en producción.

Estructura del proyecto
text
viarescate-ve/
├── api/
│   └── index.py                    # Entrypoint para Vercel
├── config/
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py                 # Configuración común
│   │   ├── development.py          # Dev local
│   │   └── production.py           # Producción (Vercel + Supabase)
│   ├── urls.py
│   ├── asgi.py
│   ├── wsgi.py
│   └── routing.py                  # Channels (si aplica)
├── core/                           # Estados, municipios, parroquias, validadores
├── usuarios/                       # Autenticación y roles
├── mapa/                           # Vistas y API del mapa
├── operaciones/                    # Centros, refugios, vías, misiones, inventario
├── templates/
│   ├── base.html
│   ├── components/
│   ├── includes/
│   ├── public/
│   ├── mapa/
│   ├── usuarios/
│   └── operaciones/
├── static/                         # Fuentes (CSS/JS sin compilar)
│   ├── css/
│   ├── js/
│   └── vendor/                     # Leaflet, etc.
├── staticfiles/                    # Salida de collectstatic (commiteado)
├── docs/
│   └── deployment.md               # Guía extendida de deploy (opcional)
├── requirements.txt
├── vercel.json
├── .env.example
├── .gitignore
├── manage.py
└── README.md
Contribuir
Hacer fork del repositorio

Crear rama: git checkout -b feature/nueva-funcionalidad

Commits con convención:

feat: nueva funcionalidad

fix: corrección de bug

docs: documentación

chore: tareas de mantenimiento

test: tests

Ejecutar tests: python manage.py test

Abrir Pull Request a main

Recursos
Repositorio: https://github.com/pedromph23/viarescate-ve

Producción: https://viarescate-ve.vercel.app

Supabase: https://supabase.com

Vercel: https://vercel.com

PostGIS: https://postgis.net

Licencia
Ver archivo LICENSE.

VíaRescate VE — Ayuda donde más se necesita.

text

---

## Cómo aplicarlo

Guarda todo lo anterior (desde `# VíaRescate VE` hasta `*Ayuda donde más se necesita.*`) en un archivo llamado `README.md` en la raíz del proyecto, o si prefieres hacerlo desde la terminal:

```bash
cd ~/proyectos/viarescate-ve
# Pega el contenido en un editor:
nano README.md
# o
code README.md
Luego commitea:

bash
git add README.md
git commit -m "docs: comprehensive README with deployment guide"
git push origin main
Listo. Un solo archivo, todo incluido.


