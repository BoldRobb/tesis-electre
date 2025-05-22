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

Crea un archivo .env en la raíz del proyecto con el siguiente contenido (ajusta los valores<vscode_annotation details='%5B%7B%22title%22%3A%22hardcoded-credentials%22%2C%22description%22%3A%22Embedding%20credentials%20in%20source%20code%20risks%20unauthorized%20access%22%7D%5D'> según</vscode_annotation> tu entorno):

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