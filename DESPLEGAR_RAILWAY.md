# Guía de Despliegue en Railway - Paso a Paso

Esta guía te llevará desde cero hasta tener tu aplicación ELECTRE III corriendo en Railway.

## ✅ Pre-requisitos completados
- [x] Librería `ELECTREIIISL.so` compilada para Linux (264 KB)
- [x] Dockerfile preparado
- [x] Código compatible con Windows y Linux

## 📋 Paso 1: Preparar el repositorio Git

```powershell
# Si no has inicializado git
git init

# Crear .gitignore para no subir archivos sensibles
@"
__pycache__/
*.pyc
.env
*.log
.venv/
venv/
.DS_Store
"@ | Out-File -FilePath .gitignore -Encoding utf8

# Añadir todos los archivos
git add .

# Primer commit
git commit -m "Preparar para Railway - incluye .so compilado"

# Crear repo en GitHub (opcional pero recomendado)
# Ve a github.com/new y crea el repositorio 'tesis-electre'
# Luego:
git remote add origin https://github.com/TU_USUARIO/tesis-electre.git
git branch -M main
git push -u origin main
```

## 🚂 Paso 2: Crear proyecto en Railway

### 2.1 Registrarse/Login
1. Ve a [railway.app](https://railway.app)
2. Click en "Login" → Continuar con GitHub
3. Autoriza Railway a acceder a tus repositorios

### 2.2 Crear nuevo proyecto
1. Click en "New Project"
2. Selecciona "Deploy from GitHub repo"
3. Busca y selecciona `tesis-electre`
4. Railway detectará automáticamente el `Dockerfile` ✅

## 🗄️ Paso 3: Añadir MySQL

1. En tu proyecto Railway, click en "+ New"
2. Selecciona "Database" → "Add MySQL"
3. Railway creará un servicio MySQL con credenciales automáticas
4. Espera 1-2 minutos a que se provisione

## 🔑 Paso 4: Configurar Variables de Entorno

### 4.1 Generar SECRET_KEY
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
**Ejemplo generado**: `LANDRF7I1s9SiRfHi2kXWF27MiZ4oyKr4C3Y8psoVR8`

### 4.2 Añadir variables en Railway
1. Click en tu servicio `tesis-electre` (el contenedor de la app)
2. Ve a la pestaña "Variables"
3. Click en "New Variable" o "Raw Editor"
4. Añade estas variables:

```env
SECRET_KEY=LANDRF7I1s9SiRfHi2kXWF27MiZ4oyKr4C3Y8psoVR8
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=11520
DLL_PATH=/app/app/dll/ELECTREIIISL.so
DEBUGGER_PATH=/app/app/dll/
API_V1_STR=/api/v1
```

### 4.3 Conectar con MySQL
Railway detecta automáticamente la conexión entre servicios. Añade estas variables usando las **referencias de Railway**:

```env
MYSQL_USER=${{MySQL.MYSQLUSER}}
MYSQL_PASSWORD=${{MySQL.MYSQLPASSWORD}}
MYSQL_HOST=${{MySQL.MYSQLHOST}}
MYSQL_PORT=${{MySQL.MYSQLPORT}}
MYSQL_DATABASE=${{MySQL.MYSQLDATABASE}}
```

**Importante**: Los valores `${{MySQL.XXXXX}}` son referencias dinámicas que Railway resuelve automáticamente. Verifica los nombres exactos en la pestaña "Variables" del servicio MySQL.

### 4.4 CORS (opcional)
Si necesitas permitir peticiones desde un frontend:
```env
BACKEND_CORS_ORIGINS=https://tu-frontend.com,https://otro-dominio.com
```

## 🚀 Paso 5: Desplegar

1. Railway desplegará automáticamente al hacer push
2. Ve a la pestaña "Deployments" para ver el progreso
3. Los logs mostrarán:
   - Construcción del Dockerfile
   - Instalación de dependencias Python
   - Inicio de Uvicorn
   - Creación de tablas en MySQL

**Tiempo estimado**: 3-5 minutos

## 🌐 Paso 6: Obtener URL pública

1. En el servicio `tesis-electre`, ve a "Settings"
2. Sección "Networking" → "Generate Domain"
3. Railway asignará un dominio tipo: `tesis-electre-production-XXXX.up.railway.app`
4. Click en "Generate Domain" y espera ~30 segundos

## ✅ Paso 7: Verificar que funciona

### 7.1 Verificar API Docs
```powershell
# Abre en tu navegador
start https://tu-app.up.railway.app/docs
```

Deberías ver la interfaz interactiva de FastAPI (Swagger UI).

### 7.2 Probar endpoint de salud
```powershell
curl https://tu-app.up.railway.app/
```

Respuesta esperada:
```json
{"message": "Sistema de Apoyo a la Toma de Decisiones API"}
```

### 7.3 Ver logs en tiempo real
```powershell
# En Railway, pestaña "Deployments" → Click en el último deploy → "View Logs"
```

## 🔍 Troubleshooting

### Error: "Application failed to respond"
**Causa**: La app no inició correctamente.
**Solución**:
1. Ve a Deployments → View Logs
2. Busca errores de Python (ImportError, etc.)
3. Verifica que todas las variables estén configuradas

### Error: "Connection refused" al conectar MySQL
**Causa**: Las variables de MySQL no están correctas.
**Solución**:
1. Ve al servicio MySQL → Variables
2. Copia los valores exactos (no las referencias `${{...}}`)
3. Verifica que el servicio MySQL esté "Active" (verde)

### Error: "libELECTREIIISL.so: cannot open shared object file"
**Causa**: El archivo .so no se copió al contenedor.
**Solución**:
1. Verifica que `app/dll/ELECTREIIISL.so` esté en tu repositorio
2. Haz commit y push nuevamente:
   ```powershell
   git add app/dll/ELECTREIIISL.so
   git commit -m "Añadir librería .so"
   git push
   ```

### La app se reinicia constantemente
**Causa**: Error en la inicialización (probablemente DB).
**Solución**:
1. Verifica logs para ver el error exacto
2. Asegúrate de que MySQL esté listo antes de que la app intente conectar
3. En `main.py`, la línea `DBInitializer.create_tables()` puede fallar si MySQL no está listo

## 📊 Monitoreo

### Ver uso de recursos
- Railway → Tu proyecto → "Metrics"
- Observa CPU, RAM y Network

### Costos
- Railway tiene un tier gratuito con $5 USD de crédito mensual
- MySQL consume ~$1-2/mes
- La app ~$1-2/mes
- **Total estimado**: $2-4/mes (dentro del tier gratuito)

## 🔄 Despliegues futuros

Cada vez que hagas push a `main`, Railway desplegará automáticamente:

```powershell
# Hacer cambios en el código
git add .
git commit -m "Descripción de cambios"
git push origin main

# Railway detectará el push y desplegará en ~3 minutos
```

## 🛠️ Railway CLI (opcional)

Para desplegar desde la terminal:

```powershell
# Instalar Railway CLI
npm i -g @railway/cli

# Login
railway login

# Vincular proyecto
railway link

# Ver logs en vivo
railway logs

# Ejecutar comando en el contenedor
railway run python -c "print('Hello from Railway')"

# Abrir shell en el contenedor
railway shell
```

## 🎯 Próximos pasos recomendados

1. **Dominio personalizado**: En Railway Settings → Domains, añade tu propio dominio
2. **Variables de entorno por ambiente**: Crea branches para staging/production
3. **Backups de MySQL**: Railway no incluye backups automáticos, considera usar Railway Volumes o exportar periódicamente
4. **Monitoreo**: Integra Sentry o Datadog para tracking de errores
5. **CI/CD avanzado**: Añade GitHub Actions para tests antes del deploy

## 📞 Soporte

- Documentación Railway: https://docs.railway.app
- Discord de Railway: https://discord.gg/railway
- Status de Railway: https://status.railway.app

---

✅ **Tu aplicación debería estar corriendo ahora en**: `https://tu-app.up.railway.app`

Prueba acceder a `/docs` para ver la documentación interactiva de FastAPI.
