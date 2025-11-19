# 🚀 Desplegar en Render.com - Guía Rápida

## ✅ Ventajas de Render
- 750 horas gratis al mes (suficiente para 1 app 24/7)
- MySQL gratis incluido
- Deploy automático desde GitHub
- SSL automático
- No requiere tarjeta de crédito

## 📝 PASOS (10 minutos)

### 1. Crear cuenta en Render
🔗 **https://render.com**
- Sign up con GitHub
- Autoriza Render a acceder a tus repos

### 2. Crear Web Service

1. Click en **"New +"** → **"Web Service"**
2. Conecta tu repositorio `tesis-electre`
3. Configura así:

```
Name: tesis-electre
Region: Oregon (US West) - o el más cercano
Branch: main
Runtime: Docker
Instance Type: Free
```

4. Click **"Create Web Service"** (no te preocupes por las variables aún)

### 3. Crear MySQL Database

1. En el Dashboard, click **"New +"** → **"MySQL"**
2. Configura:

```
Name: electre-db
Database: electre_db
User: electre_user
Region: Same as web service (Oregon)
Instance Type: Free
```

3. Click **"Create Database"**
4. Espera 2-3 minutos a que se provisione
5. Render generará credenciales automáticamente

### 4. Obtener credenciales de MySQL

1. Click en tu database `electre-db`
2. Ve a la pestaña **"Info"**
3. Copia estos valores (los necesitarás en el siguiente paso):
   - **Internal Database URL** (preferido, más rápido)
   - O individualmente: Hostname, Port, Database, Username, Password

### 5. Configurar Variables de Entorno

1. Ve a tu Web Service `tesis-electre`
2. Click en **"Environment"** en el menú lateral
3. Click **"Add Environment Variable"**
4. Añade estas variables:

#### Opción A: Usar Internal Database URL (más fácil)

Si Render te da una URL tipo `mysql://user:pass@host:port/db`:

```env
# Seguridad
SECRET_KEY=GENERA_NUEVA_CLAVE_AQUI
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=11520

# Librería
DLL_PATH=/app/app/dll/ELECTREIIISL.so
DEBUGGER_PATH=/app/app/dll/

# API
API_V1_STR=/api/v1

# MySQL - Extrae de la Internal Database URL
MYSQL_USER=electre_user
MYSQL_PASSWORD=la_password_generada
MYSQL_HOST=dpg-XXXXX-a.oregon-postgres.render.com
MYSQL_PORT=3306
MYSQL_DATABASE=electre_db
```

#### Opción B: Variables individuales de Render

Render no tiene referencias automáticas como Railway, copia manualmente:

```env
SECRET_KEY=GENERA_NUEVA_CLAVE_AQUI
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=11520
DLL_PATH=/app/app/dll/ELECTREIIISL.so
DEBUGGER_PATH=/app/app/dll/
API_V1_STR=/api/v1

# Copia estos valores de la pestaña Info de tu MySQL:
MYSQL_USER=electre_user
MYSQL_PASSWORD=<copiar de Render>
MYSQL_HOST=<copiar Hostname>
MYSQL_PORT=3306
MYSQL_DATABASE=electre_db
```

### 6. Generar SECRET_KEY

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copia el resultado y úsalo como `SECRET_KEY`.

### 7. Forzar Redeploy

1. En tu Web Service, click **"Manual Deploy"** → **"Deploy latest commit"**
2. Render reconstruirá la imagen Docker
3. Ve a **"Logs"** para monitorear el proceso (3-5 minutos)

### 8. Obtener URL Pública

Render asigna automáticamente una URL tipo:
```
https://tesis-electre.onrender.com
```

La encontrarás en la parte superior de tu Web Service.

### 9. Verificar que funciona

```powershell
# Abre la documentación interactiva
start https://tesis-electre.onrender.com/docs
```

Deberías ver Swagger UI de FastAPI ✅

---

## ⚠️ IMPORTANTE: Warm-up en Render

En el plan gratuito, tu app se "duerme" después de 15 minutos de inactividad. La primera request después de dormir tarda ~30-60 segundos.

### Solución: Keep-alive automático

Usa un servicio como **cron-job.org** o **UptimeRobot** para hacer ping cada 10 minutos:

1. Ve a https://uptimerobot.com (gratis)
2. Add New Monitor:
   - Type: HTTP(s)
   - URL: `https://tesis-electre.onrender.com/`
   - Interval: 10 minutes

---

## 🔍 Troubleshooting

### Error: "Deploy failed"
**Ver logs**:
1. Web Service → Logs
2. Busca líneas con `ERROR` o `Exception`

### Error: Can't connect to MySQL
**Solución**:
1. Verifica que el MySQL esté "Available" (verde)
2. Usa **Internal Database URL** (más rápido que external)
3. Verifica credenciales en Environment variables

### La app se reinicia constantemente
**Causa**: Probablemente error al crear tablas
**Solución**:
1. Ve a Logs
2. Si ves `Connection refused`, espera 2 minutos más a que MySQL esté listo
3. Considera añadir retry logic en `main.py`

### "Not Found" al abrir la URL
**Verifica**:
1. Que el deploy haya terminado (status "Live")
2. Que el puerto 8000 esté expuesto en el Dockerfile (ya lo está ✅)
3. Intenta `/docs` en la URL

---

## 💰 Costos

**100% GRATIS** si usas:
- 1 Web Service (750 horas/mes = suficiente para 24/7)
- 1 MySQL database (Free tier)

No requiere tarjeta de crédito.

---

## 🎯 Resumen Ultra-Rápido

```
1. render.com → Sign up con GitHub
2. New + → Web Service → tesis-electre → Docker → Free
3. New + → MySQL → electre-db → Free
4. Web Service → Environment → Añadir variables (ver arriba)
5. Manual Deploy → Deploy latest commit
6. Abrir: https://tesis-electre.onrender.com/docs
```

**Tiempo total: ~10 minutos**

---

## 📊 Comparación con Railway

| Feature | Railway | Render |
|---------|---------|--------|
| Tier gratuito | $5/mes crédito | 750 horas/mes |
| Auto-sleep | No | Sí (15 min) |
| MySQL gratis | Sí | Sí |
| Deploy automático | Sí | Sí |
| Tarjeta requerida | No | No |
| Velocidad build | ⚡⚡⚡ | ⚡⚡ |

---

## 🔄 Despliegues futuros

Cada push a `main` desplegará automáticamente:

```powershell
git add .
git commit -m "Actualización"
git push origin main
# Render detecta el push y despliega en ~3-5 minutos
```

---

## 🆘 Alternativas si Render tampoco funciona

### PythonAnywhere (muy limitado pero 100% gratis)
- No soporta Docker (requiere adaptación)
- MySQL incluido
- 512 MB RAM

### Heroku (cambió a pago en 2022)
- Ya no tiene tier gratuito ❌

### Azure App Service (requiere tarjeta)
- $200 crédito gratis primer mes
- Después cobra

---

✅ **Recomendación final**: Usar **Render.com** con **UptimeRobot** para keep-alive.

Tu app estará en: `https://tesis-electre.onrender.com`
