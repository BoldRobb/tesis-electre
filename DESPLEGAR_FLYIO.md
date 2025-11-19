# 🚀 Desplegar en Fly.io - Guía Rápida

## ✅ Ventajas de Fly.io
- 3 máquinas virtuales gratis (suficiente para app + DB)
- No se duerme (siempre activo)
- Deploy rápido
- PostgreSQL/MySQL gratis
- Certificados SSL automáticos

## ⚠️ Requiere tarjeta (no cobra en tier gratuito)

---

## 📝 PASOS (15 minutos)

### 1. Instalar Fly CLI

```powershell
# Con PowerShell
irm https://fly.io/install.ps1 | iex

# Verificar instalación
fly version
```

### 2. Crear cuenta y login

```powershell
# Abrir registro (requiere tarjeta pero no cobra)
fly auth signup

# O si ya tienes cuenta
fly auth login
```

### 3. Crear aplicación

```powershell
cd C:\Users\Roberto\Desktop\tesis\tesis-electre

# Inicializar app (detecta Dockerfile automáticamente)
fly launch

# Responde a las preguntas:
# App name: tesis-electre (o el que quieras)
# Region: Elige el más cercano (ej: mia para Miami)
# PostgreSQL: NO (usaremos MySQL)
# Redis: NO
# Deploy now: NO (configuraremos variables primero)
```

Esto creará un archivo `fly.toml` en tu proyecto.

### 4. Crear MySQL Database

Fly no tiene MySQL nativo, pero puedes usar PlanetScale (gratis) o crear tu propio MySQL en Fly:

#### Opción A: PlanetScale (recomendado, más fácil)

1. Ve a https://planetscale.com
2. Sign up (gratis, no requiere tarjeta)
3. Create database: `electre-db`
4. Get connection string
5. Copia la connection string (formato: `mysql://user:pass@host/db?sslaccept=strict`)

#### Opción B: MySQL en Fly (más control)

```powershell
# Crear volumen para persistencia
fly volumes create mysql_data --region mia --size 1

# Crear app MySQL
fly apps create electre-mysql

# Deploy MySQL
# (Necesitas un Dockerfile separado para MySQL)
```

**Para simplificar, usa PlanetScale (Opción A)** ✅

### 5. Configurar Variables (Secrets)

```powershell
# Generar SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Configurar secrets en Fly
fly secrets set SECRET_KEY="tu_clave_generada_aqui"
fly secrets set ALGORITHM="HS256"
fly secrets set ACCESS_TOKEN_EXPIRE_MINUTES="11520"
fly secrets set DLL_PATH="/app/app/dll/ELECTREIIISL.so"
fly secrets set DEBUGGER_PATH="/app/app/dll/"
fly secrets set API_V1_STR="/api/v1"

# MySQL (desde PlanetScale)
fly secrets set MYSQL_USER="tu_usuario"
fly secrets set MYSQL_PASSWORD="tu_password"
fly secrets set MYSQL_HOST="host.planetscale.com"
fly secrets set MYSQL_PORT="3306"
fly secrets set MYSQL_DATABASE="electre_db"
```

### 6. Ajustar fly.toml

Abre `fly.toml` y verifica/ajusta:

```toml
app = "tesis-electre"
primary_region = "mia"

[build]

[env]
  PORT = "8000"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = false
  auto_start_machines = true
  min_machines_running = 1

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

### 7. Desplegar

```powershell
fly deploy
```

Fly construirá la imagen Docker y desplegará (3-5 minutos).

### 8. Obtener URL

```powershell
fly status
```

Tu app estará en: `https://tesis-electre.fly.dev`

### 9. Verificar

```powershell
fly open /docs
```

Deberías ver Swagger UI ✅

---

## 🔧 Comandos Útiles

```powershell
# Ver logs en tiempo real
fly logs

# Ver status
fly status

# Abrir dashboard
fly dashboard

# SSH a la máquina
fly ssh console

# Escalar (añadir más memoria)
fly scale memory 512

# Ver secrets configurados
fly secrets list

# Detener app (para no consumir recursos)
fly scale count 0

# Reiniciar
fly scale count 1
```

---

## 🔍 Troubleshooting

### Error: "Health check failed"
**Solución**: Añadir health check al Dockerfile

Añade al final del `Dockerfile`:
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
  CMD curl -f http://localhost:8000/ || exit 1
```

Y instala curl en la imagen:
```dockerfile
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
```

### Error: "Connection to MySQL failed"
**Verifica**:
1. Que los secrets estén configurados: `fly secrets list`
2. Que PlanetScale esté activo
3. Usa la connection string SSL de PlanetScale

### La app usa mucha memoria
**Solución**: Escalar verticalmente
```powershell
fly scale memory 512
```

---

## 💰 Costos

**Tier gratuito incluye**:
- 3 máquinas compartidas (256 MB RAM cada una)
- 160 GB tráfico/mes
- Certificados SSL automáticos

**Costo real en tier gratuito**: $0

Si excedes, cobra por hora extra (~$0.01/hora).

---

## 🎯 Resumen Ultra-Rápido

```powershell
# 1. Instalar CLI
irm https://fly.io/install.ps1 | iex

# 2. Login
fly auth login

# 3. Launch
fly launch

# 4. Configurar secrets
fly secrets set SECRET_KEY="..."
fly secrets set MYSQL_USER="..."
# ... (resto de variables)

# 5. Deploy
fly deploy

# 6. Abrir
fly open /docs
```

**Tiempo total: ~15 minutos**

---

## 📊 Comparación con Render

| Feature | Render | Fly.io |
|---------|--------|--------|
| Tier gratuito | 750h/mes | 3 VMs 24/7 |
| Auto-sleep | Sí | No ⭐ |
| MySQL gratis | Sí | No (usa PlanetScale) |
| Tarjeta requerida | No | Sí |
| Velocidad | ⚡⚡ | ⚡⚡⚡ |
| Global CDN | No | Sí |

---

✅ **Usa Fly.io si**:
- No quieres auto-sleep
- Necesitas baja latencia global
- No te importa registrar tarjeta

✅ **Usa Render si**:
- No tienes tarjeta
- MySQL integrado es importante
- El auto-sleep no te molesta
