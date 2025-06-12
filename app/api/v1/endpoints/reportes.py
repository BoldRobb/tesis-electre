from typing import Any, List, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.schemas.proyecto import ProyectoCreate, ProyectoUpdate, Proyecto
from app.api import deps
from app.db.session import get_db
from app.utils.electreIII import obtener_datos_escenario_para_electre, ejecutar_electre3_desde_bd_flujo_neto, ejecutar_electre3_desde_bd_destilacion

router = APIRouter()

@router.get("/proyecto/{proyecto_id}/reporte_completo")
def obtener_reporte_completo_proyecto(
    *,
    db: Session = Depends(get_db),
    proyecto_id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Dict:
    """
    Obtener un reporte completo de todos los escenarios de un proyecto,
    incluyendo información detallada de alternativas, criterios y resultados
    de ELECTRE III con ambos métodos (destilación y flujo neto).
    
    Args:
        db: Sesión de base de datos
        proyecto_id: ID del proyecto
        current_user: Usuario autenticado
        
    Returns:
        Dict con información completa del proyecto y resultados de análisis
    """
    # Verificar que el proyecto pertenece al usuario
    proyecto = db.query(models.Proyecto).filter(
        models.Proyecto.id == proyecto_id,
        models.Proyecto.owner_id == current_user.id
    ).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    # Obtener todos los escenarios del proyecto
    escenarios = db.query(models.Escenario).filter(
        models.Escenario.proyecto_id == proyecto_id
    ).all()
    
    if not escenarios:
        raise HTTPException(status_code=404, detail="El proyecto no tiene escenarios")
    
    resultado_proyecto = {
        "proyecto": {
            "id": proyecto.id,
            "title": proyecto.title,
            "description": proyecto.description,
            "created_at": proyecto.created_at,
            "updated_at": proyecto.updated_at
        },
        "escenarios": []
    }
    
    for escenario in escenarios:
        try:
            # Obtener datos detallados del escenario para ELECTRE
            datos_electre = obtener_datos_escenario_para_electre(db, escenario.id)
            
            # Ejecutar ELECTRE III con ambos métodos
            resultado_flujo_neto = ejecutar_electre3_desde_bd_flujo_neto(db, escenario.id)
            resultado_destilacion = ejecutar_electre3_desde_bd_destilacion(db, escenario.id)
            
            # Preparar información del escenario
            escenario_info = {
                "id": escenario.id,
                "name": escenario.name,
                "description": escenario.description,
                "corte": escenario.corte,
                "created_at": escenario.created_at,
                "updated_at": escenario.updated_at,
                "criterios": [
                    {
                        "id": criterio.id,
                        "name": criterio.name,
                        "description": criterio.description,
                        "weight": criterio.weight,
                        "is_benefit": criterio.is_benefit,
                        "preference_threshold": criterio.preference_threshold,
                        "indifference_threshold": criterio.indifference_threshold,
                        "veto_threshold": criterio.veto_threshold
                    }
                    for criterio in datos_electre["criterios_obj"]
                ],
                "alternativas": [
                    {
                        "id": alternativa.id,
                        "name": alternativa.name,
                        "description": alternativa.description,
                    }
                    for alternativa in datos_electre["alternativas_obj"]
                ],
                "matriz_decision": datos_electre["matriz_decision"].tolist(),
                "resultados_electre": {
                    "flujo_neto": resultado_flujo_neto,
                    "destilacion": resultado_destilacion
                }
            }
            
            resultado_proyecto["escenarios"].append(escenario_info)
            
        except Exception as e:
            # Si hay error en un escenario, incluirlo con mensaje de error pero seguir con los demás
            escenario_info = {
                "id": escenario.id,
                "name": escenario.name,
                "description": escenario.description,
                "error": f"Error al procesar escenario: {str(e)}"
            }
            resultado_proyecto["escenarios"].append(escenario_info)
    
    return resultado_proyecto