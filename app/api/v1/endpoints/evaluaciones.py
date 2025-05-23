from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.schemas.evaluacion import EvaluacionCreate, EvaluacionUpdate, Evaluacion
from app.api import deps
from app.db.session import get_db

router = APIRouter()


@router.get("/escenario/{escenario_id}", response_model=List[Evaluacion])
def read_evaluaciones_by_escenario(
    *,
    db: Session = Depends(get_db),
    escenario_id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Obtener evaluaciones de un escenario específico
    """
    # Verificar que el escenario pertenece al usuario
    escenario = db.query(models.Escenario).join(models.Proyecto).filter(
        models.Escenario.id == escenario_id,
        models.Proyecto.owner_id == current_user.id
    ).first()
    if not escenario:
        raise HTTPException(status_code=404, detail="Escenario no encontrado")
    
    evaluaciones = db.query(models.Evaluacion).filter(
        models.Evaluacion.escenario_id == escenario_id
    ).all()
    return evaluaciones


@router.get("/alternativa/{alternativa_id}", response_model=List[Evaluacion])
def read_evaluaciones_by_alternativa(
    *,
    db: Session = Depends(get_db),
    alternativa_id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Obtener evaluaciones de una alternativa específica
    """
    # Verificar que la alternativa pertenece al usuario
    alternativa = (
        db.query(models.Alternativa)
        .join(models.Escenario)
        .join(models.Proyecto)
        .filter(
            models.Alternativa.id == alternativa_id,
            models.Proyecto.owner_id == current_user.id
        )
        .first()
    )
    if not alternativa:
        raise HTTPException(status_code=404, detail="Alternativa no encontrada")
    
    evaluaciones = db.query(models.Evaluacion).filter(
        models.Evaluacion.alternativa_id == alternativa_id
    ).all()
    return evaluaciones