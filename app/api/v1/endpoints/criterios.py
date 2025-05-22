from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.db.session import get_db

router = APIRouter()


@router.get("/escenario/{escenario_id}", response_model=List[schemas.Criterio])
def read_criterios_by_escenario(
    *,
    db: Session = Depends(get_db),
    escenario_id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Obtener criterios de un escenario específico
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
    return criterios


@router.post("/", response_model=schemas.Criterio)
def create_criterio(
    *,
    db: Session = Depends(get_db),
    criterio_in: schemas.CriterioCreate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Crear nuevo criterio
    """
    # Verificar que el escenario pertenece al usuario
    escenario = db.query(models.Escenario).join(models.Proyecto).filter(
        models.Escenario.id == criterio_in.escenario_id,
        models.Proyecto.owner_id == current_user.id
    ).first()
    if not escenario:
        raise HTTPException(status_code=404, detail="Escenario no encontrado")
    
    criterio = models.Criterio(**criterio_in.dict())
    db.add(criterio)
    db.commit()
    db.refresh(criterio)
    return criterio


@router.put("/{id}", response_model=schemas.Criterio)
def update_criterio(
    *,
    db: Session = Depends(get_db),
    id: int,
    criterio_in: schemas.CriterioUpdate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Actualizar criterio
    """
    criterio = (
        db.query(models.Criterio)
        .join(models.Escenario)
        .join(models.Proyecto)
        .filter(
            models.Criterio.id == id,
            models.Proyecto.owner_id == current_user.id
        )
        .first()
    )
    if not criterio:
        raise HTTPException(status_code=404, detail="Criterio no encontrado")
    
    criterio_data = criterio_in.dict(exclude_unset=True)
    for field in criterio_data:
        setattr(criterio, field, criterio_data[field])
    
    db.add(criterio)
    db.commit()
    db.refresh(criterio)
    return criterio


@router.get("/{id}", response_model=schemas.Criterio)
def read_criterio(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Obtener criterio por ID
    """
    criterio = (
        db.query(models.Criterio)
        .join(models.Escenario)
        .join(models.Proyecto)
        .filter(
            models.Criterio.id == id,
            models.Proyecto.owner_id == current_user.id
        )
        .first()
    )
    if not criterio:
        raise HTTPException(status_code=404, detail="Criterio no encontrado")
    return criterio


@router.delete("/{id}")
def delete_criterio(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Eliminar criterio
    """
    criterio = (
        db.query(models.Criterio)
        .join(models.Escenario)
        .join(models.Proyecto)
        .filter(
            models.Criterio.id == id,
            models.Proyecto.owner_id == current_user.id
        )
        .first()
    )
    if not criterio:
        raise HTTPException(status_code=404, detail="Criterio no encontrado")
    
    db.delete(criterio)
    db.commit()
    return {"message": "Criterio eliminado correctamente"}
