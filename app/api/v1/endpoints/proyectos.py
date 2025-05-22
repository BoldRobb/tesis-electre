from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.db.session import get_db

router = APIRouter()


@router.get("/", response_model=List[schemas.Proyecto])
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


@router.post("/", response_model=schemas.Proyecto)
def create_proyecto(
    *,
    db: Session = Depends(get_db),
    proyecto_in: schemas.ProyectoCreate,
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


@router.put("/{id}", response_model=schemas.Proyecto)
def update_proyecto(
    *,
    db: Session = Depends(get_db),
    id: int,
    proyecto_in: schemas.ProyectoUpdate,
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


@router.get("/{id}", response_model=schemas.Proyecto)
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
