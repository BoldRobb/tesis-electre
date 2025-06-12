from fastapi import APIRouter

# Importa aquí todos los routers de los endpoints de la carpeta actual
# Por ejemplo, si tienes archivos como users.py, items.py, etc.
from app.api.v1.endpoints import auth, alternativas, criterios, escenarios, evaluaciones, proyectos, electre, reportes
api_router = APIRouter()

# Incluye los routers importados
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(alternativas.router, prefix="/alternatives", tags=["alternatives"])
api_router.include_router(criterios.router, prefix="/criterios", tags=["criterios"])
api_router.include_router(escenarios.router, prefix="/escenarios", tags=["escenarios"])
api_router.include_router(evaluaciones.router, prefix="/evaluaciones", tags=["evaluaciones"])
api_router.include_router(proyectos.router, prefix="/proyectos", tags=["proyectos"])
api_router.include_router(electre.router, prefix="/electre", tags=["electre"])
api_router.include_router(reportes.router, prefix="/reportes", tags=["reportes"])
