from fastapi import APIRouter

# Importa aquí todos los routers de los endpoints de la carpeta actual
# Por ejemplo, si tienes archivos como users.py, items.py, etc.
from app.api.v1.endpoints import auth
api_router = APIRouter()

# Incluye los routers importados
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

