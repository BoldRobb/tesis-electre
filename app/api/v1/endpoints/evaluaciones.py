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

@router.post("/matriz/escenario/{escenario_id}/reinicializar", response_model=List[Evaluacion])
def reinicializar_evaluaciones_matriz(
    *,
    db: Session = Depends(get_db),
    escenario_id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Reinicializar matriz de evaluaciones: elimina todas las evaluaciones existentes 
    y crea nuevas para todas las combinaciones criterio x alternativa
    """
    # Verificar que el escenario pertenece al usuario
    escenario = db.query(models.Escenario).join(models.Proyecto).filter(
        models.Escenario.id == escenario_id,
        models.Proyecto.owner_id == current_user.id
    ).first()
    if not escenario:
        raise HTTPException(status_code=404, detail="Escenario no encontrado")
    
    # Obtener todos los criterios y alternativas del escenario
    criterios = db.query(models.Criterio).filter(
        models.Criterio.escenario_id == escenario_id
    ).all()
    
    alternativas = db.query(models.Alternativa).filter(
        models.Alternativa.escenario_id == escenario_id
    ).all()
    
    if not criterios:
        raise HTTPException(status_code=400, detail="El escenario no tiene criterios")
    
    if not alternativas:
        raise HTTPException(status_code=400, detail="El escenario no tiene alternativas")
    
    # Eliminar todas las evaluaciones existentes del escenario
    evaluaciones_existentes = db.query(models.Evaluacion).filter(
        models.Evaluacion.escenario_id == escenario_id
    ).all()
    
    for evaluacion in evaluaciones_existentes:
        db.delete(evaluacion)
    
    # Crear todas las nuevas combinaciones
    nuevas_evaluaciones = []
    for criterio in criterios:
        for alternativa in alternativas:
            evaluacion = models.Evaluacion(
                criterio_id=criterio.id,
                alternativa_id=alternativa.id,
                escenario_id=escenario_id,
                valor=0.0  # Valor por defecto
            )
            db.add(evaluacion)
            nuevas_evaluaciones.append(evaluacion)
    
    db.commit()
    
    # Refrescar todas las evaluaciones para obtener sus IDs
    for evaluacion in nuevas_evaluaciones:
        db.refresh(evaluacion)
    
    return nuevas_evaluaciones

@router.get("/criterio/{criterio_id}", response_model=List[Evaluacion])
def read_evaluaciones_by_criterio(
    *,
    db: Session = Depends(get_db),
    criterio_id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Obtener evaluaciones de un criterio específico
    """
    # Verificar que el criterio pertenece al usuario
    criterio = (
        db.query(models.Criterio)
        .join(models.Escenario)
        .join(models.Proyecto)
        .filter(
            models.Criterio.id == criterio_id,
            models.Proyecto.owner_id == current_user.id
        )
        .first()
    )
    if not criterio:
        raise HTTPException(status_code=404, detail="Criterio no encontrado")
    
    evaluaciones = db.query(models.Evaluacion).filter(
        models.Evaluacion.criterio_id == criterio_id
    ).all()
    return evaluaciones


@router.put("/matriz/escenario/{escenario_id}", response_model=List[Evaluacion])
def update_evaluaciones_matriz(
    *,
    db: Session = Depends(get_db),
    escenario_id: int,
    evaluaciones_data: List[EvaluacionUpdate],
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Actualizar múltiples evaluaciones de la matriz de un escenario
    """
    # Verificar que el escenario pertenece al usuario
    escenario = db.query(models.Escenario).join(models.Proyecto).filter(
        models.Escenario.id == escenario_id,
        models.Proyecto.owner_id == current_user.id
    ).first()
    if not escenario:
        raise HTTPException(status_code=404, detail="Escenario no encontrado")
    
    # Obtener todas las evaluaciones del escenario
    evaluaciones_existentes = db.query(models.Evaluacion).filter(
        models.Evaluacion.escenario_id == escenario_id
    ).all()
    
    if not evaluaciones_existentes:
        raise HTTPException(
            status_code=404, 
            detail="No existen evaluaciones para este escenario. Use el endpoint de creación de matriz."
        )
    
    # Crear un diccionario para búsqueda rápida por criterio_id y alternativa_id
    evaluaciones_dict = {
        (eval.criterio_id, eval.alternativa_id): eval 
        for eval in evaluaciones_existentes
    }
    
    evaluaciones_actualizadas = []
    
    for eval_data in evaluaciones_data:
        # Buscar la evaluación correspondiente
        key = (eval_data.criterio_id, eval_data.alternativa_id)
        evaluacion = evaluaciones_dict.get(key)
        
        if not evaluacion:
            raise HTTPException(
                status_code=404, 
                detail=f"No se encontró evaluación para criterio {eval_data.criterio_id} y alternativa {eval_data.alternativa_id}"
            )
        
        # Actualizar los campos proporcionados
        eval_dict = eval_data.dict(exclude_unset=True)
        for field, value in eval_dict.items():
            if field not in ['criterio_id', 'alternativa_id']:  # No permitir cambiar estas claves
                setattr(evaluacion, field, value)
        
        evaluaciones_actualizadas.append(evaluacion)
    
    db.commit()
    
    # Refrescar todas las evaluaciones actualizadas
    for evaluacion in evaluaciones_actualizadas:
        db.refresh(evaluacion)
    
    return evaluaciones_actualizadas


@router.post("/matriz/escenario/{escenario_id}", response_model=List[Evaluacion])
def create_evaluaciones_matriz(
    *,
    db: Session = Depends(get_db),
    escenario_id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Crear matriz completa de evaluaciones para un escenario (todas las combinaciones de criterios x alternativas)
    """
    # Verificar que el escenario pertenece al usuario
    escenario = db.query(models.Escenario).join(models.Proyecto).filter(
        models.Escenario.id == escenario_id,
        models.Proyecto.owner_id == current_user.id
    ).first()
    if not escenario:
        raise HTTPException(status_code=404, detail="Escenario no encontrado")
    
    # Obtener todos los criterios y alternativas del escenario
    criterios = db.query(models.Criterio).filter(
        models.Criterio.escenario_id == escenario_id
    ).all()
    
    alternativas = db.query(models.Alternativa).filter(
        models.Alternativa.escenario_id == escenario_id
    ).all()
    
    if not criterios:
        raise HTTPException(status_code=400, detail="El escenario no tiene criterios")
    
    if not alternativas:
        raise HTTPException(status_code=400, detail="El escenario no tiene alternativas")
    
    # Verificar si ya existen evaluaciones para evitar duplicados
    evaluaciones_existentes = db.query(models.Evaluacion).filter(
        models.Evaluacion.escenario_id == escenario_id
    ).all()
    
    if evaluaciones_existentes:
        raise HTTPException(
            status_code=400, 
            detail="Ya existen evaluaciones para este escenario. Use el endpoint de actualización individual."
        )
    
    # Crear todas las combinaciones
    nuevas_evaluaciones = []
    for criterio in criterios:
        for alternativa in alternativas:
            evaluacion = models.Evaluacion(
                criterio_id=criterio.id,
                alternativa_id=alternativa.id,
                escenario_id=escenario_id,
                valor=0.0  # Valor por defecto, puede ser cambiado después
            )
            db.add(evaluacion)
            nuevas_evaluaciones.append(evaluacion)
    
    db.commit()
    
    # Refrescar todas las evaluaciones para obtener sus IDs
    for evaluacion in nuevas_evaluaciones:
        db.refresh(evaluacion)
    
    return nuevas_evaluaciones


@router.post("/", response_model=Evaluacion)
def create_evaluacion(
    *,
    db: Session = Depends(get_db),
    evaluacion_in: EvaluacionCreate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Crear nueva evaluación
    """
    # Verificar que tanto la alternativa como el criterio pertenecen al usuario
    alternativa = (
        db.query(models.Alternativa)
        .join(models.Escenario)
        .join(models.Proyecto)
        .filter(
            models.Alternativa.id == evaluacion_in.alternativa_id,
            models.Proyecto.owner_id == current_user.id
        )
        .first()
    )
    if not alternativa:
        raise HTTPException(status_code=404, detail="Alternativa no encontrada")
    
    criterio = (
        db.query(models.Criterio)
        .join(models.Escenario)
        .join(models.Proyecto)
        .filter(
            models.Criterio.id == evaluacion_in.criterio_id,
            models.Proyecto.owner_id == current_user.id
        )
        .first()
    )
    if not criterio:
        raise HTTPException(status_code=404, detail="Criterio no encontrado")
    
    # Verificar que la alternativa y el criterio pertenecen al mismo escenario
    if alternativa.escenario_id != criterio.escenario_id:
        raise HTTPException(
            status_code=400, 
            detail="La alternativa y el criterio deben pertenecer al mismo escenario"
        )
    
    evaluacion = models.Evaluacion(**evaluacion_in.dict())
    db.add(evaluacion)
    db.commit()
    db.refresh(evaluacion)
    return evaluacion


@router.put("/{id}", response_model=Evaluacion)
def update_evaluacion(
    *,
    db: Session = Depends(get_db),
    id: int,
    evaluacion_in: EvaluacionUpdate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Actualizar evaluación
    """
    evaluacion = (
        db.query(models.Evaluacion)
        .join(models.Alternativa)
        .join(models.Escenario)
        .join(models.Proyecto)
        .filter(
            models.Evaluacion.id == id,
            models.Proyecto.owner_id == current_user.id
        )
        .first()
    )
    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    
    evaluacion_data = evaluacion_in.dict(exclude_unset=True)
    for field in evaluacion_data:
        setattr(evaluacion, field, evaluacion_data[field])
    
    db.add(evaluacion)
    db.commit()
    db.refresh(evaluacion)
    return evaluacion


@router.get("/{id}", response_model=Evaluacion)
def read_evaluacion(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Obtener evaluación por ID
    """
    evaluacion = (
        db.query(models.Evaluacion)
        .join(models.Alternativa)
        .join(models.Escenario)
        .join(models.Proyecto)
        .filter(
            models.Evaluacion.id == id,
            models.Proyecto.owner_id == current_user.id
        )
        .first()
    )
    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    return evaluacion


@router.delete("/{id}")
def delete_evaluacion(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Eliminar evaluación
    """
    evaluacion = (
        db.query(models.Evaluacion)
        .join(models.Alternativa)
        .join(models.Escenario)
        .join(models.Proyecto)
        .filter(
            models.Evaluacion.id == id,
            models.Proyecto.owner_id == current_user.id
        )
        .first()
    )
    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    
    db.delete(evaluacion)
    db.commit()
    return {"message": "Evaluación eliminada correctamente"}

@router.post("/matriz/escenario/{escenario_id}/completar", response_model=List[Evaluacion])
def completar_evaluaciones_matriz(
    *,
    db: Session = Depends(get_db),
    escenario_id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Completa la matriz de evaluaciones para un escenario:
    - Si la evaluación existe, la deja igual.
    - Si no existe, la crea con valor 0.
    """
    # Verificar que el escenario pertenece al usuario
    escenario = db.query(models.Escenario).join(models.Proyecto).filter(
        models.Escenario.id == escenario_id,
        models.Proyecto.owner_id == current_user.id
    ).first()
    if not escenario:
        raise HTTPException(status_code=404, detail="Escenario no encontrado")
    
    criterios = db.query(models.Criterio).filter(
        models.Criterio.escenario_id == escenario_id
    ).all()
    alternativas = db.query(models.Alternativa).filter(
        models.Alternativa.escenario_id == escenario_id
    ).all()
    
    if not criterios or not alternativas:
        raise HTTPException(status_code=400, detail="El escenario debe tener criterios y alternativas")
    
    # Obtener todas las evaluaciones existentes en el escenario
    evaluaciones_existentes = db.query(models.Evaluacion).filter(
        models.Evaluacion.escenario_id == escenario_id
    ).all()
    eval_dict = {
        (e.criterio_id, e.alternativa_id): e for e in evaluaciones_existentes
    }
    
    nuevas_evaluaciones = []
    for criterio in criterios:
        for alternativa in alternativas:
            key = (criterio.id, alternativa.id)
            if key not in eval_dict:
                evaluacion = models.Evaluacion(
                    criterio_id=criterio.id,
                    alternativa_id=alternativa.id,
                    escenario_id=escenario_id,
                    value=0.0
                )
                db.add(evaluacion)
                nuevas_evaluaciones.append(evaluacion)
    
    db.commit()
    
    # Devolver todas las evaluaciones del escenario (existentes y nuevas)
    todas = db.query(models.Evaluacion).filter(
        models.Evaluacion.escenario_id == escenario_id
    ).all()
    return todas