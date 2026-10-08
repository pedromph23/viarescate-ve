# VíaRescate VE

Sistema inteligente de rutas para la distribución de ayuda humanitaria en Venezuela.

VíaRescate VE es una aplicación web desarrollada con **Django/GeoDjango** para apoyar la gestión de operaciones humanitarias, información territorial, recursos, vehículos, refugios, reportes viales y planificación de rutas.

> **Estado actual:** proyecto funcional en desarrollo progresivo. Este README documenta el entorno local actualmente verificado y la arquitectura existente. No se consideran terminadas funcionalidades que todavía estén en desarrollo.

---

# 1. Descripción del proyecto

VíaRescate VE tiene como objetivo proporcionar una plataforma para apoyar la planificación y gestión de operaciones de ayuda humanitaria en Venezuela.

El sistema combina:

* Información territorial de Venezuela.
* Información geográfica.
* Mapas interactivos.
* Gestión de operaciones.
* Gestión de recursos.
* Gestión de inventarios.
* Gestión de vehículos.
* Gestión de refugios.
* Gestión de centros de ayuda.
* Reportes sobre vías.
* Evaluación del estado de las vías.
* Cálculo y evaluación de rutas.
* Auditoría de operaciones.
* API para funcionalidades operativas.
* PostgreSQL/PostGIS para almacenamiento geoespacial.

El proyecto se desarrolla de forma progresiva para evitar romper las funcionalidades existentes.

---

# 2. Tecnologías utilizadas

## Backend

* Python
* Django
* Django REST Framework
* GeoDjango

## Base de datos

* PostgreSQL
* PostGIS

## Frontend

* HTML
* CSS
* JavaScript
* Leaflet
* GeoJSON

## Infraestructura

* Windows
* WSL 2
* Debian / Ubuntu
* Visual Studio Code
* Git
* GitHub
* Render
* Supabase
* Gunicorn

## Tecnologías contempladas progresivamente

* Redis
* Celery
* Django Channels
* ASGI
* Optimización de rutas
* Servicios externos de routing
* OSRM

---

# 3. Arquitectura general

La arquitectura general del proyecto se puede representar de la siguiente manera:

```text
Windows
   │
   └── WSL 2
        │
        └── Linux
             │
             ├── Git
             ├── Python
             ├── Django
             ├── PostgreSQL
             ├── PostGIS
             └── VíaRescate VE
                    │
                    ├── GeoDjango
                    ├── API
                    ├── Mapas
                    ├── Operaciones
                    └── Routing
```

Para producción:

```text
                    ┌──────────────┐
                    │    Usuario   │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │    Render    │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Django /     │
                    │ GeoDjango    │
                    └──────┬───────┘
                           │
                           ▼
                 ┌────────────────────┐
                 │ Supabase PostgreSQL│
                 │      + PostGIS     │
                 └────────────────────┘
```

GitHub funciona como repositorio principal del código fuente.

---

# 4. Requisitos para desarrollo local

Para desarrollar VíaRescate VE en Windows se recomienda utilizar:

* Windows 10 versión 2004 o superior, o Windows 11.
* WSL 2.
* Una distribución Linux.
* Visual Studio Code.
* Git.
* Python.
* PostgreSQL.
* PostGIS.

Microsoft recomienda actualmente utilizar:

```powershell
wsl --install
```

para instalar WSL y una distribución Linux.

---

# 5. Instalación de WSL 2 en Windows

## 5.1. ¿Qué es WSL?

WSL significa:

```text
Windows Subsystem for Linux
```

Permite ejecutar una distribución Linux directamente dentro de Windows y utilizar Bash, Git, Python, PostgreSQL y otras herramientas Linux sin tener que instalar una máquina virtual tradicional ni realizar un arranque dual.

Para VíaRescate VE, WSL permite tener un entorno Linux de desarrollo mientras se mantiene Windows como sistema operativo principal.

---

# 6. Comprobar la versión de Windows

Antes de instalar WSL:

Presionar:

```text
Windows + R
```

Escribir:

```text
winver
```

Presionar:

```text
Enter
```

Se recomienda Windows 11 o Windows 10 versión 2004/build 19041 o posterior.

---

# 7. Instalar WSL desde PowerShell

Abrir:

```text
Inicio
→ PowerShell
→ Ejecutar como administrador
```

Ejecutar:

```powershell
wsl --install
```

Este comando instala los componentes necesarios de WSL y configura WSL 2 como versión predeterminada. En una instalación normal también instala Ubuntu como distribución predeterminada.

Después de ejecutar el comando puede ser necesario reiniciar Windows.

---

# 8. Reiniciar Windows

Reiniciar el equipo:

```text
Inicio → Reiniciar
```

Después del reinicio, Windows puede continuar automáticamente con la instalación de Linux.

---

# 9. Crear el usuario de Linux

La primera vez que se inicia la distribución Linux aparecerá una terminal solicitando:

```text
Enter new UNIX username:
```

Introducir un nombre de usuario.

Por ejemplo:

```text
pedro
```

Después solicitará:

```text
New password:
```

Escribir una contraseña.

> Al escribir la contraseña en Linux no aparecerán caracteres en pantalla. Es normal.

Confirmar la contraseña.

Al terminar aparecerá una terminal similar a:

```text
pedro@DESKTOP-XXXX:~$
```

Esto significa que Linux dentro de WSL está funcionando.

---

# 10. Comprobar WSL

Desde PowerShell:

```powershell
wsl --status
```

También:

```powershell
wsl --list --verbose
```

o:

```powershell
wsl -l -v
```

Debe aparecer la distribución instalada y la columna:

```text
VERSION
2
```

Microsoft documenta `wsl --list --verbose` como comando para comprobar las distribuciones instaladas y si están utilizando WSL 1 o WSL 2.

Ejemplo:

```text
NAME      STATE           VERSION
Debian    Running         2
```

o:

```text
Ubuntu    Running         2
```

---

# 11. Instalar una distribución específica

Si se desea consultar las distribuciones disponibles:

```powershell
wsl --list --online
```

También:

```powershell
wsl -l -o
```

Para instalar una distribución específica:

```powershell
wsl --install -d Debian
```

o:

```powershell
wsl --install -d Ubuntu
```

Microsoft permite especificar la distribución mediante `-d`.

---

# 12. Recomendación para VíaRescate VE

El desarrollo actual de VíaRescate VE fue realizado en un entorno:

```text
Debian GNU/Linux 13 (trixie)
```

Por lo tanto, Debian es una opción válida para reproducir el entorno utilizado actualmente.

Ejemplo:

```powershell
wsl --install -d Debian
```

Después abrir:

```text
Debian
```

desde el menú Inicio de Windows.

---

# 13. Actualizar Linux

Dentro de la terminal Linux:

```bash
sudo apt update
```

Después:

```bash
sudo apt upgrade -y
```

Recomendado:

```bash
sudo apt update && sudo apt upgrade -y
```

---

# 14. Instalar herramientas básicas

En Debian/Ubuntu:

```bash
sudo apt install -y \
    git \
    curl \
    wget \
    build-essential \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev
```

Comprobar:

```bash
git --version
```

```bash
python3 --version
```

```bash
pip3 --version
```

---

# 15. Instalar Visual Studio Code

Instalar Visual Studio Code en Windows desde su instalador oficial.

Después instalar la extensión:

```text
WSL
```

de Microsoft.

La extensión permite abrir el proyecto almacenado en Linux directamente desde VS Code y ejecutar Python/Django dentro del entorno WSL.

Microsoft recomienda utilizar VS Code junto con WSL para desarrollar y depurar aplicaciones dentro del entorno Linux.

---

# 16. Abrir VíaRescate VE con VS Code

Desde la terminal Linux:

```bash
cd ~/proyectos/viarescate-ve
```

Después:

```bash
code .
```

Si `code` está correctamente configurado, VS Code se abrirá conectado al entorno WSL.

En VS Code debe aparecer que está conectado a WSL.

---

# 17. Crear la carpeta de proyectos

Si todavía no existe:

```bash
mkdir -p ~/proyectos
```

Entrar:

```bash
cd ~/proyectos
```

---

# 18. Clonar VíaRescate VE

Repositorio:

```text
https://github.com/pedromph23/viarescate-ve.git
```

Clonar:

```bash
git clone https://github.com/pedromph23/viarescate-ve.git
```

Entrar:

```bash
cd viarescate-ve
```

Comprobar:

```bash
git status
```

---

# 19. Crear entorno virtual Python

Dentro del proyecto:

```bash
python3 -m venv .venv
```

Activar:

```bash
source .venv/bin/activate
```

La terminal debe mostrar algo parecido a:

```text
(.venv) pedro@DESKTOP-XXXX:~/proyectos/viarescate-ve$
```

---

# 20. Actualizar pip

Con el entorno virtual activo:

```bash
python -m pip install --upgrade pip
```

---

# 21. Instalar dependencias de VíaRescate VE

```bash
pip install -r requirements.txt
```

Si se actualizan las dependencias:

```bash
pip install --upgrade -r requirements.txt
```

---

# 22. PostgreSQL y PostGIS

VíaRescate VE utiliza PostgreSQL junto con PostGIS.

El backend de Django utiliza:

```python
django.contrib.gis.db.backends.postgis
```

Por este motivo PostGIS es obligatorio para el funcionamiento geoespacial del proyecto.

---

# 23. Instalar PostgreSQL

En Debian/Ubuntu:

```bash
sudo apt update
```

Después:

```bash
sudo apt install -y postgresql postgresql-contrib
```

Comprobar:

```bash
psql --version
```

---

# 24. Iniciar PostgreSQL

En WSL:

```bash
sudo service postgresql start
```

Comprobar:

```bash
sudo service postgresql status
```

El entorno local actualmente verificado muestra:

```text
postgresql.service - PostgreSQL RDBMS
Active: active
```

---

# 25. Crear usuario PostgreSQL

Entrar como administrador:

```bash
sudo -u postgres psql
```

Crear usuario:

```sql
CREATE USER viarescate WITH PASSWORD 'TU_PASSWORD_LOCAL';
```

---

# 26. Crear base de datos

Crear:

```sql
CREATE DATABASE viarescate_ve OWNER viarescate;
```

Conectarse:

```sql
\c viarescate_ve
```

---

# 27. Instalar y habilitar PostGIS

Dentro de PostgreSQL:

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

Comprobar:

```sql
SELECT PostGIS_Version();
```

La versión actualmente verificada en el entorno local es:

```text
3.5
```

Salir:

```sql
\q
```

---

# 28. Configurar `.env`

Copiar:

```bash
cp .env.example .env
```

Editar:

```bash
nano .env
```

Configuración recomendada para una instalación nueva:

```env
DB_NAME=viarescate_ve
DB_USER=viarescate
DB_PASSWORD=TU_PASSWORD_LOCAL
DB_HOST=127.0.0.1
DB_PORT=5432
```

Guardar el archivo.

> **Importante:** `.env` no debe subirse a GitHub.

---

# 29. Configuración actual del entorno local

En el entorno local verificado actualmente existe:

```text
DB_NAME=viarescate_ve
DB_HOST=127.0.0.1
DB_PORT=5432
```

La configuración local actualmente funcional utiliza el usuario PostgreSQL definido en `.env`.

El archivo `.env.example` utiliza:

```env
DB_USER=viarescate
```

Mientras que la configuración local actualmente verificada utiliza:

```env
DB_USER=postgres
```

No cambiar una configuración local funcional sin comprobar primero la contraseña del usuario `viarescate`.

---

# 30. Configuración de Django

La configuración principal se encuentra en:

```text
config/settings/base.py
```

El backend utiliza:

```python
django.contrib.gis.db.backends.postgis
```

La conexión utiliza las variables:

```text
DB_NAME
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT
```

---

# 31. Verificar Django

Con el entorno virtual activo:

```bash
python manage.py check
```

Resultado esperado:

```text
System check identified no issues (0 silenced).
```

El entorno local actualmente verificado devuelve exactamente ese resultado.

---

# 32. Migraciones

Crear migraciones después de modificar modelos:

```bash
python manage.py makemigrations
```

Aplicar:

```bash
python manage.py migrate
```

Ver estado:

```bash
python manage.py showmigrations
```

Comprobar operaciones pendientes:

```bash
python manage.py migrate --plan
```

Si no hay migraciones pendientes:

```text
Planned operations: No planned migration operations.
```

---

# 33. Estado actual de migraciones

En el entorno local verificado:

* Las migraciones están aplicadas.
* Django no presenta errores de configuración.
* No existen operaciones pendientes.
* `mapa` actualmente no tiene migraciones propias.

---

# 34. Datos territoriales de Venezuela

La base local contiene información territorial real de Venezuela.

Registros actualmente verificados:

| Tabla            | Registros |
| ---------------- | --------: |
| `core_estado`    |        24 |
| `core_municipio` |       335 |
| `core_parroquia` |     1.134 |

Por tanto:

```text
24 estados
335 municipios
1.134 parroquias
```

Estos datos territoriales deben conservarse al realizar limpiezas de datos ficticios de operaciones.

---

# 35. Cargar datos territoriales

Si la base de datos está vacía y el comando está disponible:

```bash
python manage.py load_territorial_data
```

Después comprobar:

```bash
python manage.py shell
```

También puede verificarse directamente desde PostgreSQL.

---

# 36. Verificar datos desde PostgreSQL

Conectarse:

```bash
psql -h 127.0.0.1 -U postgres -d viarescate_ve
```

Ejecutar:

```sql
SELECT COUNT(*) FROM core_estado;
```

```sql
SELECT COUNT(*) FROM core_municipio;
```

```sql
SELECT COUNT(*) FROM core_parroquia;
```

Valores actualmente verificados:

```text
core_estado      = 24
core_municipio   = 335
core_parroquia   = 1134
```

---

# 37. Tablas actuales

La base local actualmente contiene:

```text
auth_group
auth_group_permissions
auth_permission
core_estado
core_municipio
core_parroquia
django_admin_log
django_content_type
django_migrations
django_session
operaciones_auditlog
operaciones_centroayuda
operaciones_inventario
operaciones_mision
operaciones_movimientoinventario
operaciones_recurso
operaciones_refugio
operaciones_reportevial
operaciones_vehiculo
operaciones_via
spatial_ref_sys
usuarios_usuario
usuarios_usuario_groups
usuarios_usuario_user_permissions
```

La tabla:

```text
spatial_ref_sys
```

pertenece a PostGIS.

---

# 38. Crear superusuario

Ejecutar:

```bash
python manage.py createsuperuser
```

Seguir las instrucciones.

---

# 39. Ejecutar VíaRescate VE

Activar el entorno:

```bash
cd ~/proyectos/viarescate-ve
source .venv/bin/activate
```

Ejecutar:

```bash
python manage.py runserver
```

Abrir en Windows:

```text
http://127.0.0.1:8000/
```

Administrador:

```text
http://127.0.0.1:8000/admin/
```

Detener:

```text
Ctrl + C
```

---

# 40. Flujo completo de instalación

Una instalación nueva puede seguir este flujo:

```text
Windows
   ↓
Instalar WSL 2
   ↓
Instalar Debian/Ubuntu
   ↓
Actualizar Linux
   ↓
Instalar Git
   ↓
Instalar Python
   ↓
Instalar VS Code + extensión WSL
   ↓
Clonar GitHub
   ↓
Crear .venv
   ↓
Instalar requirements.txt
   ↓
Instalar PostgreSQL
   ↓
Instalar/configurar PostGIS
   ↓
Crear viarescate_ve
   ↓
Configurar .env
   ↓
Ejecutar migrate
   ↓
Cargar datos territoriales
   ↓
Crear superusuario
   ↓
Ejecutar runserver
   ↓
Probar aplicación
```

---

# 41. Estructura del proyecto

La estructura principal es:

```text
viarescate-ve/
│
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── production.py
│   │   └── __init__.py
│   │
│   ├── asgi.py
│   ├── urls.py
│   ├── wsgi.py
│   └── __init__.py
│
├── core/
│
├── usuarios/
│
├── mapa/
│
├── operaciones/
│   ├── api/
│   └── routing/
│
├── data/
│   └── territorial/
│
├── static/
│
├── templates/
│
├── .env.example
├── manage.py
├── requirements.txt
├── render.yaml
└── README.md
```

---

# 42. Aplicación `core`

El módulo `core` contiene principalmente la información territorial y modelos centrales del sistema.

Actualmente incluye información de:

```text
Estados
Municipios
Parroquias
```

La información geográfica utiliza las capacidades de GeoDjango/PostGIS cuando corresponde.

---

# 43. Aplicación `usuarios`

El módulo:

```text
usuarios/
```

gestiona los usuarios del sistema y la integración con las funcionalidades de autenticación/autorización de Django.

---

# 44. Aplicación `mapa`

El módulo:

```text
mapa/
```

contiene funcionalidades relacionadas con la visualización geográfica.

La interfaz utiliza tecnologías como:

```text
Leaflet
GeoJSON
JavaScript
GeoDjango/PostGIS
```

---

# 45. Aplicación `operaciones`

El módulo:

```text
operaciones/
```

concentra funcionalidades operativas.

Entre ellas:

* Centros de ayuda.
* Inventarios.
* Misiones.
* Movimientos de inventario.
* Recursos.
* Refugios.
* Reportes viales.
* Vehículos.
* Vías.
* Auditoría.

---

# 46. Sistema de rutas

El sistema posee una estructura:

```text
operaciones/routing/
```

para gestionar proveedores y servicios relacionados con rutas.

Existe integración/proceso de trabajo con proveedores como:

```text
OSRM
```

La evaluación de rutas puede considerar el estado de las vías.

---

# 47. Estados de las vías

El sistema contempla estados como:

```text
NORMAL
PRECAUCION
AFECTADA
CRITICA
CERRADA
```

Estos estados permiten evaluar la transitabilidad de las rutas.

---

# 48. Estados de reportes viales

Los reportes pueden utilizar estados como:

```text
CONFIRMADO
PENDIENTE
RECHAZADO
RESUELTO
```

Esto permite diferenciar información reportada de información validada.

---

# 49. Auditoría

Existe funcionalidad de auditoría.

La base de datos contiene:

```text
operaciones_auditlog
```

La auditoría debe utilizarse para registrar acciones relevantes dentro de la aplicación.

No debe utilizarse para almacenar información sensible innecesaria.

---

# 50. API

La aplicación cuenta con una estructura API:

```text
operaciones/api/
```

Antes de modificar una API utilizada por el frontend deben comprobarse:

* URL.
* Método HTTP.
* Parámetros.
* Serializadores.
* Permisos.
* Respuesta JSON.
* Vistas.
* Consumo JavaScript.

---

# 51. Git y GitHub

Comprobar estado:

```bash
git status
```

Ver ramas:

```bash
git branch
```

Actualizar:

```bash
git pull origin main
```

Agregar cambios:

```bash
git add .
```

Crear commit:

```bash
git commit -m "descripcion del cambio"
```

Subir:

```bash
git push origin main
```

---

# 52. Ejemplos de commits

```text
feat: agregar gestión de refugios
```

```text
fix: corregir mapa público
```

```text
fix: corregir cálculo de rutas
```

```text
docs: actualizar README
```

```text
refactor: reorganizar servicios de operaciones
```

```text
chore: actualizar dependencias
```

---

# 53. `.gitignore`

El proyecto debe evitar subir archivos temporales y secretos.

Especialmente:

```text
.env
.venv/
__pycache__/
*.pyc
```

No se deben subir contraseñas, tokens ni claves privadas.

---

# 54. Seguridad

Nunca subir a GitHub:

```text
.env
contraseñas
tokens
SECRET_KEY reales
credenciales PostgreSQL
credenciales SMTP
claves privadas
archivos .pem
archivos .key
```

Antes de hacer:

```bash
git push
```

revisar:

```bash
git status
```

y:

```bash
git diff --cached
```

---

# 55. Regla para cambios de base de datos

Los cambios estructurales deben seguir:

```text
models.py
    ↓
makemigrations
    ↓
migrate
    ↓
pruebas
```

No se recomienda modificar manualmente las tablas de producción para cambios que deberían estar representados mediante modelos y migraciones de Django.

---

# 56. Desarrollo progresivo

VíaRescate VE debe desarrollarse de manera incremental.

Antes de modificar una funcionalidad existente:

1. Revisar el código actual.
2. Identificar dependencias.
3. Revisar modelos.
4. Revisar URLs.
5. Revisar APIs.
6. Revisar templates.
7. Revisar JavaScript.
8. Realizar el cambio.
9. Ejecutar `python manage.py check`.
10. Ejecutar migraciones si corresponde.
11. Probar localmente.
12. Hacer commit.
13. Subir a GitHub.
14. Verificar Render.

No realizar una reescritura completa cuando una modificación puntual sea suficiente.

---

# 57. Producción

El despliegue previsto utiliza:

```text
GitHub
   ↓
Render
   ↓
Django / GeoDjango
   ↓
Supabase PostgreSQL + PostGIS
```

Render ejecuta Django utilizando Gunicorn.

La configuración de producción se encuentra separada de la configuración de desarrollo.

---

# 58. Configuración de Django

El proyecto separa:

```text
config/settings/base.py
config/settings/development.py
config/settings/production.py
```

Esto permite mantener configuraciones diferentes para:

```text
Desarrollo local
```

y:

```text
Producción
```

---

# 59. Render

El proyecto contiene:

```text
render.yaml
```

La aplicación está preparada para ejecutarse con:

```text
gunicorn config.wsgi:application
```

Las variables sensibles deben configurarse en Render y no en el repositorio.

---

# 60. Supabase

Supabase se utiliza como infraestructura PostgreSQL/PostGIS para producción.

La conexión debe configurarse mediante variables de entorno.

No almacenar directamente en GitHub:

* contraseña de Supabase;
* claves privadas;
* tokens;
* secretos;
* credenciales de conexión.

---

# 61. Desarrollo local vs producción

## Desarrollo

```text
Windows
  ↓
WSL 2
  ↓
Linux
  ↓
PostgreSQL/PostGIS local
  ↓
Django
```

## Producción

```text
Internet
  ↓
Render
  ↓
Django
  ↓
Supabase PostgreSQL/PostGIS
```

---

# 62. Comandos de diagnóstico

## WSL

Desde PowerShell:

```powershell
wsl --status
```

```powershell
wsl -l -v
```

## PostgreSQL

```bash
sudo service postgresql status
```

## Django

```bash
python manage.py check
```

## Migraciones

```bash
python manage.py showmigrations
```

```bash
python manage.py migrate --plan
```

## Git

```bash
git status
```

```bash
git log --oneline -5
```

---

# 63. Solución de problemas de WSL

## `wsl --install` muestra la ayuda

Microsoft indica que si WSL ya está instalado, `wsl --install` puede mostrar la ayuda en lugar de instalar una distribución.

Consultar:

```powershell
wsl --list --online
```

Después:

```powershell
wsl --install -d Debian
```

o:

```powershell
wsl --install -d Ubuntu
```

---

## La instalación se queda en 0.0 %

Puede utilizarse:

```powershell
wsl --install --web-download -d Debian
```

Microsoft documenta esta alternativa para descargar la distribución desde una fuente en línea cuando la instalación normal se bloquea.

---

# 64. Solución de problemas de PostgreSQL

Si PostgreSQL no está iniciado:

```bash
sudo service postgresql start
```

Comprobar:

```bash
sudo service postgresql status
```

Comprobar versión:

```bash
psql --version
```

---

# 65. Solución de problemas de conexión

Comprobar las variables:

```text
DB_NAME
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT
```

La configuración local utiliza:

```text
DB_HOST=127.0.0.1
DB_PORT=5432
```

Probar:

```bash
psql -h 127.0.0.1 -U postgres -d viarescate_ve
```

---

# 66. Solución de problemas de PostGIS

Conectarse:

```bash
psql -h 127.0.0.1 -U postgres -d viarescate_ve
```

Ejecutar:

```sql
SELECT PostGIS_Version();
```

Si la extensión no existe:

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

---

# 67. Solución de problemas de Django

Ejecutar:

```bash
python manage.py check
```

Después:

```bash
python manage.py migrate --plan
```

Si se modificaron modelos:

```bash
python manage.py makemigrations
```

Después:

```bash
python manage.py migrate
```

---

# 68. Verificación local actual

El entorno local de VíaRescate VE fue verificado con:

```text
Sistema:
Debian GNU/Linux 13 (trixie)

PostgreSQL:
Activo

Puerto:
5432

Base:
viarescate_ve

Codificación:
UTF8

PostGIS:
3.5

Django backend:
django.contrib.gis.db.backends.postgis

Host:
127.0.0.1

Migraciones:
Aplicadas

Migraciones pendientes:
Ninguna

Django check:
Sin errores
```

Datos territoriales:

```text
Estados:     24
Municipios:  335
Parroquias:  1.134
```

---

# 69. Instalación rápida desde cero

Para reproducir el entorno:

## Windows / PowerShell como administrador

```powershell
wsl --install -d Debian
```

Reiniciar Windows si lo solicita.

Abrir Debian.

## Linux / WSL

```bash
sudo apt update
sudo apt upgrade -y
```

Instalar herramientas:

```bash
sudo apt install -y \
    git \
    curl \
    wget \
    build-essential \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    postgresql \
    postgresql-contrib
```

Crear carpeta:

```bash
mkdir -p ~/proyectos
cd ~/proyectos
```

Clonar:

```bash
git clone https://github.com/pedromph23/viarescate-ve.git
cd viarescate-ve
```

Crear entorno:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instalar dependencias:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Iniciar PostgreSQL:

```bash
sudo service postgresql start
```

Crear base:

```bash
sudo -u postgres psql
```

Dentro:

```sql
CREATE USER viarescate WITH PASSWORD 'TU_PASSWORD_LOCAL';
CREATE DATABASE viarescate_ve OWNER viarescate;
\c viarescate_ve
CREATE EXTENSION IF NOT EXISTS postgis;
SELECT PostGIS_Version();
\q
```

Configurar:

```bash
cp .env.example .env
nano .env
```

Aplicar migraciones:

```bash
python manage.py migrate
```

Cargar territorio:

```bash
python manage.py load_territorial_data
```

Crear administrador:

```bash
python manage.py createsuperuser
```

Comprobar:

```bash
python manage.py check
```

Ejecutar:

```bash
python manage.py runserver
```

Abrir:

```text
http://127.0.0.1:8000/
```

---

# 70. Flujo de trabajo diario recomendado

Cada vez que se vaya a trabajar en el proyecto:

```bash
cd ~/proyectos/viarescate-ve
```

Activar entorno:

```bash
source .venv/bin/activate
```

Actualizar código:

```bash
git pull origin main
```

Comprobar:

```bash
python manage.py check
```

Trabajar en VS Code:

```bash
code .
```

Después de realizar cambios:

```bash
python manage.py check
```

Si se modificaron modelos:

```bash
python manage.py makemigrations
python manage.py migrate
```

Probar:

```bash
python manage.py runserver
```

Después:

```bash
git status
```

Agregar:

```bash
git add .
```

Commit:

```bash
git commit -m "descripcion del cambio"
```

Push:

```bash
git push origin main
```

---

# 71. Próximos pasos del proyecto

La evolución del proyecto puede continuar progresivamente con:

1. Consolidación del mapa público y administrativo.
2. Reutilización de servicios geográficos.
3. Mejoras de visualización con Leaflet.
4. Gestión avanzada de vías.
5. Evaluación de rutas.
6. Optimización de distribución de ayuda.
7. Gestión avanzada de recursos.
8. Mejoras en auditoría.
9. Pruebas automatizadas.
10. Mejoras de seguridad.
11. Optimización del despliegue.
12. Integración progresiva de Celery y Redis.
13. Integración progresiva de ASGI/Channels.
14. Mejoras de monitoreo y operación.

---

# 72. Reglas importantes del proyecto

### No modificar producción directamente

Los cambios de esquema deben pasar por:

```text
models.py
→ makemigrations
→ migrate
```

### No subir secretos

Nunca:

```text
.env
passwords
tokens
private keys
```

### No romper funcionalidades existentes

Antes de modificar una funcionalidad:

```text
revisar
→ cambiar
→ comprobar
→ probar
→ desplegar
```

### Mantener datos territoriales reales

Los datos de:

```text
Estados
Municipios
Parroquias
```

son datos territoriales reales y deben conservarse.

Los datos ficticios de pruebas operativas pueden limpiarse de forma controlada.

---

# 73. Referencias oficiales

Documentación oficial de Microsoft sobre WSL:

https://learn.microsoft.com/es-es/windows/wsl/install

Documentación sobre configuración de entornos de desarrollo con WSL:

https://learn.microsoft.com/es-es/windows/wsl/setup/environment

Documentación de comandos de WSL:

https://learn.microsoft.com/windows/wsl/basic-commands

---

# 74. Proyecto

Repositorio:

https://github.com/pedromph23/viarescate-ve

VíaRescate VE:

**Sistema inteligente de rutas para distribución de ayuda humanitaria en Venezuela.**

Desarrollado progresivamente con:

```text
Django
GeoDjango
PostgreSQL
PostGIS
Leaflet
GitHub
Render
Supabase
WSL
```

