# 🚀 CHECKLIST FINAL - Despliegue Railway

## ✅ Estado Actual
- [x] Librería `ELECTREIIISL.so` compilada (264 KB)
- [x] Dockerfile configurado
- [x] Código compatible Windows/Linux
- [x] Variables de entorno preparadas
- [x] Commit creado: "Preparar para Railway"

## 📝 PASOS SIGUIENTES (5 minutos)

### 1. Push a GitHub (si aún no lo hiciste)
```powershell
# Si no tienes remoto configurado
git remote add origin https://github.com/TU_USUARIO/tesis-electre.git

# Push
git push -u origin main
```

### 2. Ir a Railway
🔗 **https://railway.app**

1. Login con GitHub
2. Click "New Project"
3. Selecciona "Deploy from GitHub repo"
4. Busca `tesis-electre`
5. Railway empezará a construir automáticamente ✅

### 3. Añadir MySQL (mientras construye)
1. En tu proyecto, click "+ New"
2. "Database" → "Add MySQL"
3. Espera 1-2 minutos a que se provisione

### 4. Configurar Variables (IMPORTANTE)
Click en el servicio `tesis-electre` → pestaña "Variables" → "Raw Editor"

Copia y pega esto (ajusta el SECRET_KEY):

```env
SECRET_KEY=LANDRF7I1s9SiRfHi2kXWF27MiZ4oyKr4C3Y8psoVR8
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=11520
DLL_PATH=/app/app/dll/ELECTREIIISL.so
DEBUGGER_PATH=/app/app/dll/
API_V1_STR=/api/v1
MYSQL_USER=${{MySQL.MYSQLUSER}}
MYSQL_PASSWORD=${{MySQL.MYSQLPASSWORD}}
MYSQL_HOST=${{MySQL.MYSQLHOST}}
MYSQL_PORT=${{MySQL.MYSQLPORT}}
MYSQL_DATABASE=${{MySQL.MYSQLDATABASE}}
```

⚠️ **IMPORTANTE**: Genera un nuevo SECRET_KEY:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. Generar Dominio Público
1. En el servicio `tesis-electre` → "Settings"
2. Sección "Networking" → "Generate Domain"
3. Railway te dará una URL tipo: `tesis-electre-production-XXXX.up.railway.app`

### 6. Verificar que funciona
```powershell
# Reemplaza con tu URL de Railway
start https://tu-app.up.railway.app/docs
```

Deberías ver la documentación interactiva de FastAPI (Swagger UI) ✅

## 🎯 Resumen Ultra-Rápido

```powershell
# 1. Push a GitHub
git push -u origin main

# 2. Ve a railway.app
#    - Login con GitHub
#    - New Project → Deploy from GitHub → tesis-electre
#    - Add MySQL
#    - Variables → pega las variables de arriba
#    - Generate Domain

# 3. Abre tu app
start https://tu-app.up.railway.app/docs
```

## 📊 Tiempos Estimados
- Push a GitHub: 30 segundos
- Build en Railway: 3-5 minutos
- Provisionar MySQL: 1-2 minutos
- Configurar variables: 2 minutos
- **TOTAL: ~8 minutos**

## 🆘 Si algo falla

### La app no inicia
```powershell
# En Railway → Deployments → Click en el último → "View Logs"
# Busca líneas con ERROR o Exception
```

### Error de MySQL
1. Verifica que el servicio MySQL esté "Active" (verde)
2. Verifica que las variables `${{MySQL.XXXXX}}` tengan los nombres correctos
3. En la pestaña Variables del MySQL, copia los nombres exactos

### No encuentra el .so
```powershell
# Verifica que esté en el repo
git ls-files | Select-String "ELECTREIIISL.so"

# Si no aparece, añádelo
git add app/dll/ELECTREIIISL.so -f
git commit -m "Añadir librería .so"
git push
```

## 📚 Documentación Completa
Lee `DESPLEGAR_RAILWAY.md` para la guía detallada con capturas y troubleshooting avanzado.

## 🎉 ¡Listo!
Tu app ELECTRE III estará en producción en Railway, accesible públicamente y con MySQL configurado.

**URL final**: `https://tesis-electre-production-XXXX.up.railway.app`
