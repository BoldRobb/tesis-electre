from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.schemas.proyecto import ProyectoCreate, ProyectoUpdate, Proyecto
from app.api import deps
from app.db.session import get_db

router = APIRouter()


@router.get("/", response_model=List[Proyecto])
def read_proyectos(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Obtener proyectos del usuario actual
    """
    proyectos = db.query(models.Proyecto).filter(
        models.Proyecto.owner_id == current_user.id
    ).offset(skip).limit(limit).all()
    return proyectos


@router.post("/", response_model=Proyecto)
def create_proyecto(
    *,
    db: Session = Depends(get_db),
    proyecto_in: ProyectoCreate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Crear nuevo proyecto
    """
    proyecto = models.Proyecto(**proyecto_in.dict(), owner_id=current_user.id)
    db.add(proyecto)
    db.commit()
    db.refresh(proyecto)
    return proyecto


@router.put("/{id}", response_model=Proyecto)
def update_proyecto(
    *,
    db: Session = Depends(get_db),
    id: int,
    proyecto_in: ProyectoUpdate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Actualizar proyecto
    """
    proyecto = db.query(models.Proyecto).filter(
        models.Proyecto.id == id,
        models.Proyecto.owner_id == current_user.id
    ).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    proyecto_data = proyecto_in.dict(exclude_unset=True)
    for field in proyecto_data:
        setattr(proyecto, field, proyecto_data[field])
    
    db.add(proyecto)
    db.commit()
    db.refresh(proyecto)
    return proyecto


@router.get("/{id}", response_model=Proyecto)
def read_proyecto(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Obtener proyecto por ID
    """
    proyecto = db.query(models.Proyecto).filter(
        models.Proyecto.id == id,
        models.Proyecto.owner_id == current_user.id
    ).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return proyecto


@router.delete("/{id}")
def delete_proyecto(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Eliminar proyecto
    """
    proyecto = db.query(models.Proyecto).filter(
        models.Proyecto.id == id,
        models.Proyecto.owner_id == current_user.id
    ).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    db.delete(proyecto)
    db.commit()
    return {"message": "Proyecto eliminado correctamente"}

@router.post("/{id}/clonar", response_model=Proyecto)
def clonar_proyecto(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Clona un proyecto con todos sus escenarios, criterios, alternativas y evaluaciones.
    """
    # Obtener el proyecto original
    proyecto = db.query(models.Proyecto).filter(
        models.Proyecto.id == id,
        models.Proyecto.owner_id == current_user.id
    ).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    # Crear el nuevo proyecto (clon)
    nuevo_proyecto = models.Proyecto(
        title=f"Copia de {proyecto.title}",
        description=proyecto.description,
        owner_id=current_user.id,
    )
    db.add(nuevo_proyecto)
    db.flush()  # Para obtener el id del nuevo proyecto

    for escenario in proyecto.escenarios:
        nuevo_escenario = models.Escenario(
            name=escenario.name,
            description=escenario.description,
            proyecto_id=nuevo_proyecto.id
        )
        db.add(nuevo_escenario)
        db.flush()

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
    db.refresh(nuevo_proyecto)
    return nuevo_proyecto