# Hosting y despliegue (resumen)

Este archivo explica cómo construir y ejecutar la aplicación usando Docker/Docker Compose, y qué considerar respecto a las librerías C++ (.dll/.so) y el `.env`.

Requisitos previos
- Tener instalado `docker` y `docker-compose`.
- Si trabajas en Windows, recomiendo usar WSL2 para mejor compatibilidad con contenedores Linux.

Archivos añadidos
- `Dockerfile` – imagen basada en `python:3.11-slim`, instala `g++`, `cmake`, `build-essential` y dependencias comunes.
- `Dockerfile.build-cpp` – versión del Dockerfile preparada para compilar código C++ desde fuente (multi-stage build).
- `docker-compose.yml` – levanta el servicio `app` y un servicio `db` con MySQL 8.
- `.env.example` – variables de entorno que debes rellenar y guardar como `.env`.
- `railway.json` – configuración opcional de Railway (healthcheck, comandos).
- `COMPILAR_CPP_LINUX.md` – guía detallada para compilar la librería C++ como `.so` para Linux.

Pasos rápidos (PowerShell)
```powershell
# Copia el ejemplo de .env y rellena los valores sensibles
cp .env.example .env
# (Editar .env con valores reales)

docker-compose up --build -d
# Ver logs
docker-compose logs -f app
# Parar
docker-compose down
```

Notas sobre `.env`
- La app usa `pydantic` y `Settings.Config.env_file = ".env"`, por lo que al iniciar el contenedor la app cargará `./.env`.
- Nunca subas tu `.env` con `SECRET_KEY` o contraseñas a repositorios públicos.

Librerías C++ y binarios nativos
- En el repo hay `app/dll/ELECTREIIISL.dll` y `app/dll/libELECTREIIISL.a`.
- Los archivos `.dll` son binarios de Windows; para ejecutar en un contenedor Linux necesitas una versión `.so` (shared object) compatible con Linux o compilar la librería dentro de la imagen.

Opciones para manejar las librerías nativas:
1) Usar versiones Linux (.so)
   - Si tienes el código fuente de la librería, añade pasos en el `Dockerfile` para compilarla (ejemplo en la sección "Compilar desde fuente").
   - Luego ajusta `DLL_PATH` en `.env` a la ruta del `.so` en el contenedor.

2) Compilar dentro del contenedor (si hay fuente)
   - `Dockerfile` ya instala `g++` y `cmake`. Añade comandos `RUN cmake ... && make` para generar `libelectre.so`.

3) Ejecutar en Windows (local) o usar una imagen Windows Container
   - Si dependes exclusivamente de `ELECTREIIISL.dll` y no tienes `.so`, considera desplegar en Windows Server containers o compilar una versión Linux.

Ejemplo mínimo para compilar desde fuente (añádelo al Dockerfile si tienes el código):
```dockerfile
# después de instalar build-essential y cmake
COPY cpp-src /tmp/cpp-src
WORKDIR /tmp/cpp-src
RUN mkdir build && cd build && cmake .. && make && cp lib*/libelectre*.so /usr/local/lib/
```

Problemas frecuentes
- Error al conectar con MySQL: asegúrate de que las variables en `.env` están correctas y que `db` ya está up cuando la app intente crear tablas.
- Librería nativa no encontrada: revisa `DLL_PATH` y permisos; dentro del contenedor ejecuta `ldd <archivo>` para ver dependencias (si es `.so`).

## Desplegar en Railway

Railway detecta automáticamente el `Dockerfile` y construye la imagen. Sigue estos pasos:

### 1. Preparar el proyecto
```powershell
# Asegúrate de tener un repositorio Git
git init
git add .
git commit -m "Initial commit"
```

### 2. Crear proyecto en Railway
1. Ve a [railway.app](https://railway.app) y regístrate/inicia sesión con GitHub.
2. Click en "New Project" → "Deploy from GitHub repo".
3. Selecciona tu repositorio `tesis-electre`.
4. Railway detectará el `Dockerfile` automáticamente.

### 3. Agregar base de datos MySQL
1. En tu proyecto Railway, click en "+ New" → "Database" → "Add MySQL".
2. Railway creará un servicio MySQL y generará credenciales automáticamente.

### 4. Configurar variables de entorno
1. Click en tu servicio `app` → pestaña "Variables".
2. Añade estas variables (Railway provee las de MySQL automáticamente si conectas los servicios):

```
SECRET_KEY=genera_una_clave_segura_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=11520

MYSQL_USER=${{MySQL.MYSQLUSER}}
MYSQL_PASSWORD=${{MySQL.MYSQLPASSWORD}}
MYSQL_HOST=${{MySQL.MYSQLHOST}}
MYSQL_PORT=${{MySQL.MYSQLPORT}}
MYSQL_DATABASE=${{MySQL.MYSQLDATABASE}}

DLL_PATH=/app/app/dll/ELECTREIIISL.dll
DEBUGGER_PATH=/app/app/dll/

API_V1_STR=/api/v1
```

**Nota importante**: Railway usa variables de referencia como `${{MySQL.MYSQLUSER}}` que conectan automáticamente con el servicio MySQL. Verifica los nombres exactos en la pestaña "Variables" del servicio MySQL.

### 5. Generar SECRET_KEY seguro
```powershell
# En PowerShell, genera una clave aleatoria
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 6. Desplegar
Railway desplegará automáticamente al hacer push al repositorio. Cada commit en la rama principal desplegará una nueva versión.

```powershell
git add .
git commit -m "Configure for Railway"
git push origin main
```

### 7. Monitorear el despliegue
- Ve a la pestaña "Deployments" para ver logs en tiempo real.
- Railway asignará un dominio público automáticamente (ej: `tu-app.up.railway.app`).
- Accede a `/docs` para ver la API interactiva de FastAPI.

### Problemas comunes en Railway

**1. Librería C++ (.dll) no compatible**
- Railway usa contenedores Linux. Si `ELECTREIIISL.dll` es Windows-only, necesitas:
  - Compilar una versión Linux (.so) de la librería, o
  - Usar Wine (complejo y no recomendado para producción)

**2. Error de conexión a MySQL**
- Verifica que las variables `${{MySQL.*}}` estén correctamente referenciadas.
- Asegúrate de que ambos servicios estén en la misma red (Railway los conecta automáticamente).

**3. Puerto incorrecto**
- Railway detecta automáticamente el puerto 8000 del `Dockerfile`. No necesitas variable `PORT` adicional.

**4. Timeout al iniciar**
- Si la app tarda en crear tablas, Railway podría matar el proceso. Añade un health check o incrementa el timeout en Settings.

### Alternativa: Railway CLI
```powershell
# Instalar Railway CLI
npm i -g @railway/cli

# Login
railway login

# Crear proyecto
railway init

# Enlazar base de datos
railway add --database mysql

# Desplegar
railway up
```

### Costo
- Railway ofrece un tier gratuito con $5 de crédito mensual.
- MySQL consume recursos; monitorea el uso en el dashboard.

---

Siguientes pasos recomendados
- Si quieres, preparo un `Dockerfile` alternativo que compile la librería desde su código fuente (si me proporcionas la carpeta/fuentes C++).
- Puedo añadir un `healthcheck` en `docker-compose.yml` o un `wait-for-it` para retrasar el arranque de la app hasta que MySQL acepte conexiones.

