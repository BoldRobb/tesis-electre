from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.schemas.escenario import EscenarioCreate, EscenarioUpdate, Escenario
from app.api import deps
from app.db.session import get_db

router = APIRouter()


@router.get("/proyecto/{proyecto_id}", response_model=List[Escenario])
def read_escenarios_by_proyecto(
    *,
    db: Session = Depends(get_db),
    proyecto_id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Obtener escenarios de un proyecto específico
    """
    # Verificar que el proyecto pertenece al usuario
    proyecto = db.query(models.Proyecto).filter(
        models.Proyecto.id == proyecto_id,
        models.Proyecto.owner_id == current_user.id
    ).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    escenarios = db.query(models.Escenario).filter(
        models.Escenario.proyecto_id == proyecto_id
    ).all()
    return escenarios


@router.post("/", response_model=Escenario)
def create_escenario(
    *,
    db: Session = Depends(get_db),
    escenario_in: EscenarioCreate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Crear nuevo escenario
    """
    # Verificar que el proyecto pertenece al usuario
    proyecto = db.query(models.Proyecto).filter(
        models.Proyecto.id == escenario_in.proyecto_id,
        models.Proyecto.owner_id == current_user.id
    ).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    escenario = models.Escenario(**escenario_in.dict())
    db.add(escenario)
    db.commit()
    db.refresh(escenario)
    return escenario


@router.put("/{id}", response_model=Escenario)
def update_escenario(
    *,
    db: Session = Depends(get_db),
    id: int,
    escenario_in: EscenarioUpdate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Actualizar escenario
    """
    escenario = db.query(models.Escenario).join(models.Proyecto).filter(
        models.Escenario.id == id,
        models.Proyecto.owner_id == current_user.id
    ).first()
    if not escenario:
        raise HTTPException(status_code=404, detail="Escenario no encontrado")
    
    escenario_data = escenario_in.dict(exclude_unset=True)
    for field in escenario_data:
        setattr(escenario, field, escenario_data[field])
    
    db.add(escenario)
    db.commit()
    db.refresh(escenario)
    return escenario


@router.get("/{id}", response_model=Escenario)
def read_escenario(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Obtener escenario por ID
    """
    escenario = db.query(models.Escenario).join(models.Proyecto).filter(
        models.Escenario.id == id,
        models.Proyecto.owner_id == current_user.id
    ).first()
    if not escenario:
        raise HTTPException(status_code=404, detail="Escenario no encontrado")
    return escenario


@router.delete("/{id}")
def delete_escenario(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Eliminar escenario
    """
    escenario = db.query(models.Escenario).join(models.Proyecto).filter(
        models.Escenario.id == id,
        models.Proyecto.owner_id == current_user.id
    ).first()
    if not escenario:
        raise HTTPException(status_code=404, detail="Escenario no encontrado")
    
    db.delete(escenario)
    db.commit()
    return {"message": "Escenario eliminado correctamente"}

@router.post("/{id}/clonar", response_model=Escenario)
def clonar_escenario(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Clona un escenario con sus alternativas, criterios y evaluaciones.
    """
    # Obtener el escenario original
    escenario = db.query(models.Escenario).join(models.Proyecto).filter(
        models.Escenario.id == id,
        models.Proyecto.owner_id == current_user.id
    ).first()
    if not escenario:
        raise HTTPException(status_code=404, detail="Escenario no encontrado")

    # Crear el nuevo escenario (clon)
    nuevo_escenario = models.Escenario(
        name=f"Copia de {escenario.name}",
        description=escenario.description,
        proyecto_id=escenario.proyecto_id
    )
    db.add(nuevo_escenario)
    db.flush()  # Para obtener el id del nuevo escenario

    # Mapear criterios originales a nuevos
    criterio_id_map = {}
    for criterio in escenario.criterios:
        nuevo_criterio = models.Criterio(
            name=criterio.name,
            description=criterio.description,
            weight=criterio.weight,
            is_benefit=criterio.is_benefit,
            escenario_id=nuevo_escenario.id,
            preference_threshold=criterio.preference_threshold,
            indifference_threshold=criterio.indifference_threshold,
            veto_threshold=criterio.veto_threshold
        )
        db.add(nuevo_criterio)
        db.flush()
        criterio_id_map[criterio.id] = nuevo_criterio.id

    # Mapear alternativas originales a nuevas
    alternativa_id_map = {}
    for alternativa in escenario.alternativas:
        nueva_alternativa = models.Alternativa(
            name=alternativa.name,
            description=alternativa.description,
            escenario_id=nuevo_escenario.id
        )
        db.add(nueva_alternativa)
        db.flush()
        alternativa_id_map[alternativa.id] = nueva_alternativa.id

    # Clonar evaluaciones usando los nuevos IDs
    for evaluacion in escenario.evaluaciones:
        nueva_evaluacion = models.Evaluacion(
            value=evaluacion.value,
            escenario_id=nuevo_escenario.id,
            alternativa_id=alternativa_id_map.get(evaluacion.alternativa_id),
            criterio_id=criterio_id_map.get(evaluacion.criterio_id)
        )
        db.add(nueva_evaluacion)

    db.commit()
    db.refresh(nuevo_escenario)
    return nuevo_escenario