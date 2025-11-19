# Compilar ELECTREIIISL para Linux

Esta guía explica cómo compilar tu librería C++ `ELECTREIIISL.dll` (Windows) como `.so` (Linux) para usar en el contenedor Docker.

## Prerrequisitos

Necesitas el **código fuente C++** de la librería ELECTREIIISL. Si solo tienes el `.dll` y el `.a`, necesitarás acceso al código original.

## Estructura esperada del código fuente

Coloca tu código fuente C++ en una carpeta, por ejemplo:
```
cpp-src/
├── CMakeLists.txt          # (opción 1: usar CMake)
├── Makefile                # (opción 2: Makefile tradicional)
├── electre.cpp             # Código principal
├── electre.h               # Headers
└── ... (otros archivos .cpp/.h)
```

## Opción 1: Compilar con CMake (recomendado)

### 1. Crear CMakeLists.txt

Si no tienes uno, crea `cpp-src/CMakeLists.txt`:

```cmake
cmake_minimum_required(VERSION 3.10)
project(ELECTREIIISL)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Añade aquí todos tus archivos .cpp
add_library(ELECTREIIISL SHARED
    electre.cpp
    # añade más archivos si los tienes
)

# Si necesitas enlazar otras librerías (ej: math)
target_link_libraries(ELECTREIIISL m)

# Instalar la librería
install(TARGETS ELECTREIIISL
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin)
```

### 2. Compilar localmente (en Linux o WSL)

```bash
cd cpp-src
mkdir build && cd build
cmake ..
make
# Esto genera libELECTREIIISL.so
ls -la libELECTREIIISL.so
```

### 3. Copiar el .so al proyecto

```bash
cp build/libELECTREIIISL.so ../app/dll/
```

## Opción 2: Compilar con g++ directamente

Si tu proyecto es simple (uno o pocos archivos):

```bash
cd cpp-src
g++ -shared -fPIC -o libELECTREIIISL.so electre.cpp -lm
cp libELECTREIIISL.so ../app/dll/
```

### Flags importantes:
- `-shared`: crea una librería compartida (.so)
- `-fPIC`: Position Independent Code (requerido para .so)
- `-lm`: enlaza librería matemática estándar
- `-std=c++11`: si usas características de C++11 o superior

## Opción 3: Compilar dentro del Dockerfile (automático)

Esta es la mejor opción para producción. Modifica el `Dockerfile`:

```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar herramientas de compilación C/C++
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    g++ \
    cmake \
    pkg-config \
    libffi-dev \
    libssl-dev \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ============================================
# COMPILAR LIBRERÍA C++ ELECTREIIISL
# ============================================
COPY cpp-src /tmp/cpp-src
WORKDIR /tmp/cpp-src

# Opción A: con CMake
RUN mkdir build && cd build && \
    cmake .. && \
    make && \
    mkdir -p /app/app/dll && \
    cp build/libELECTREIIISL.so /app/app/dll/

# Opción B: con g++ directo (comentar si usas CMake)
# RUN g++ -shared -fPIC -o libELECTREIIISL.so electre.cpp -lm && \
#     mkdir -p /app/app/dll && \
#     cp libELECTREIIISL.so /app/app/dll/

# Limpiar archivos temporales
RUN rm -rf /tmp/cpp-src

# ============================================
# INSTALAR DEPENDENCIAS PYTHON
# ============================================
WORKDIR /app
COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r /app/requirements.txt

# Copiar el resto de la app
COPY . /app

# Dar permisos
RUN chmod -R a+rX /app/app/dll

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Actualizar .env para Linux

Cambia la extensión en tu `.env`:

```env
# Linux (contenedor Docker / Railway)
DLL_PATH=/app/app/dll/libELECTREIIISL.so
DEBUGGER_PATH=/app/app/dll/

# Windows (desarrollo local)
# DLL_PATH=C:/Users/Roberto/Desktop/tesis/tesis-electre/app/dll/ELECTREIIISL.dll
# DEBUGGER_PATH=C:/Users/Roberto/Desktop/tesis/tesis-electre/app/dll/
```

## Modificar código Python para compatibilidad

El código Python actual usa `os.add_dll_directory()` que es específico de Windows. Para hacerlo compatible con Linux:

**En `app/utils/electreIII.py`**, reemplaza las secciones que cargan la DLL:

```python
import ctypes
import platform
from app.core.config import settings

# Cargar la librería de forma compatible
if platform.system() == 'Windows':
    os.add_dll_directory(settings.DEBUGGER_PATH)
    dll = ctypes.CDLL(settings.DLL_PATH)
else:
    # Linux/Unix
    dll = ctypes.CDLL(settings.DLL_PATH)
```

## Verificar que funciona

Una vez compilado, verifica la librería:

```bash
# En Linux/WSL
ldd /app/app/dll/libELECTREIIISL.so
# Debe mostrar las dependencias (libstdc++, libc, libm, etc.)

# Verificar símbolos exportados
nm -D /app/app/dll/libELECTREIIISL.so | grep ElectreIII
# Debe mostrar las funciones como ElectreIIIExplotarFlujoNeto
```

## Problemas comunes

### Error: "undefined symbol"
- Verifica que todas las funciones estén declaradas con `extern "C"` en el código C++:
```cpp
extern "C" {
    const char* ElectreIIIExplotarFlujoNeto(long numAlternativas, ...);
}
```

### Error: "cannot open shared object file"
- Añade la ruta al `LD_LIBRARY_PATH`:
```bash
export LD_LIBRARY_PATH=/app/app/dll:$LD_LIBRARY_PATH
```

O en el Dockerfile:
```dockerfile
ENV LD_LIBRARY_PATH=/app/app/dll:$LD_LIBRARY_PATH
```

### Error al compilar: "missing header"
- Instala las dependencias necesarias en el Dockerfile:
```dockerfile
RUN apt-get install -y libboost-dev  # ejemplo
```

## Próximos pasos

1. Coloca tu código fuente C++ en la carpeta `cpp-src/`
2. Crea el `CMakeLists.txt` o usa compilación directa con g++
3. Actualiza el `Dockerfile` con la sección de compilación
4. Modifica `electreIII.py` para compatibilidad cross-platform
5. Actualiza tu `.env` con la ruta `.so`
6. Prueba localmente con Docker:
   ```bash
   docker build -t tesis-electre .
   docker run -p 8000:8000 --env-file .env tesis-electre
   ```
7. Despliega en Railway (detectará automáticamente el Dockerfile actualizado)

---

Si compartes tu código fuente C++ puedo crear automáticamente el `CMakeLists.txt` optimizado y actualizar el Dockerfile completo.
