# Sistema de Apoyo a la Toma de Decisiones - FastAPI

Este proyecto es una API desarrollada con **FastAPI** y **SQLAlchemy** para la gestión de proyectos, escenarios, criterios, alternativas y evaluaciones, utilizando una base de datos MySQL.

---

## 1. Requisitos previos

- Python 3.9 o superior
- MySQL Server
- [pip](https://pip.pypa.io/en/stable/)

---

## 2. Instalación de dependencias

Instala los paquetes necesarios ejecutando:

```bash
pip install -r requirements.txt
```
## 3. Configuración de variables de entorno

Crea un archivo .env en la raíz del proyecto con el siguiente contenido (ajusta los valores según tu entorno):
```bash
MYSQL_USER=tu_usuario
MYSQL_PASSWORD=tu_contraseña
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=electre
SECRET_KEY=tu_clave_secreta
```
Nota: Puedes modificar otros valores en app/core/config.py según tus necesidades.

## 4. Configuración de la base de datos
Asegúrate de que tu base de datos MySQL esté corriendo y que el usuario y la base de datos existan.

Puedes crear la base de datos con:

## 5. Ejecución de la API
Inicia el servidor de desarrollo con:

```bash
uvicorn main:app --reload
```
La API estará disponible en: http://localhost:8000

La documentación interactiva estará en: http://localhost:8000/docs

## 6. Notas adicionales
Si cambias la configuración de la base de datos, reinicia el servidor.
Para producción, revisa la configuración de CORS y seguridad en main.py y .env.

¡Listo! Ya puedes comenzar a utilizar tu API con FastAPI y MySQL.