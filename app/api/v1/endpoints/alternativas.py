from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.schemas.alternativa import AlternativaCreate, AlternativaUpdate, Alternativa

from app.api import deps
from app.db.session import get_db

router = APIRouter()


@router.get("/escenario/{escenario_id}", response_model=List[Alternativa])
def read_alternativas_by_escenario(
    *,
    db: Session = Depends(get_db),
    escenario_id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Obtener alternativas de un escenario específico
    """
    # Verificar que el escenario pertenece al usuario
    escenario = db.query(models.Escenario).join(models.Proyecto).filter(
        models.Escenario.id == escenario_id,
        models.Proyecto.owner_id == current_user.id
    ).first()
    if not escenario:
        raise HTTPException(status_code=404, detail="Escenario no encontrado")
    
    alternativas = db.query(models.Alternativa).filter(
        models.Alternativa.escenario_id == escenario_id
    ).all()
    return alternativas


@router.post("/", response_model=Alternativa)
def create_alternativa(
    *,
    db: Session = Depends(get_db),
    alternativa_in: AlternativaCreate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Crear nueva alternativa
    """
    # Verificar que el escenario pertenece al usuario
    escenario = db.query(models.Escenario).join(models.Proyecto).filter(
        models.Escenario.id == alternativa_in.escenario_id,
        models.Proyecto.owner_id == current_user.id
    ).first()
    if not escenario:
        raise HTTPException(status_code=404, detail="Escenario no encontrado")
    
    alternativa = models.Alternativa(**alternativa_in.dict())
    db.add(alternativa)
    db.commit()
    db.refresh(alternativa)
    return alternativa


@router.put("/{id}", response_model=Alternativa)
def update_alternativa(
    *,
    db: Session = Depends(get_db),
    id: int,
    alternativa_in: AlternativaUpdate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Actualizar alternativa
    """
    alternativa = (
        db.query(models.Alternativa)
        .join(models.Escenario)
        .join(models.Proyecto)
        .filter(
            models.Alternativa.id == id,
            models.Proyecto.owner_id == current_user.id
        )
        .first()
    )
    if not alternativa:
        raise HTTPException(status_code=404, detail="Alternativa no encontrada")
    
    alternativa_data = alternativa_in.dict(exclude_unset=True)
    for field in alternativa_data:
        setattr(alternativa, field, alternativa_data[field])
    
    db.add(alternativa)
    db.commit()
    db.refresh(alternativa)
    return alternativa


@router.get("/{id}", response_model=Alternativa)
def read_alternativa(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Obtener alternativa por ID
    """
    alternativa = (
        db.query(models.Alternativa)
        .join(models.Escenario)
        .join(models.Proyecto)
        .filter(
            models.Alternativa.id == id,
            models.Proyecto.owner_id == current_user.id
        )
        .first()
    )
    if not alternativa:
        raise HTTPException(status_code=404, detail="Alternativa no encontrada")
    return alternativa


@router.delete("/{id}")
def delete_alternativa(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Eliminar alternativa
    """
    alternativa = (
        db.query(models.Alternativa)
        .join(models.Escenario)
        .join(models.Proyecto)
        .filter(
            models.Alternativa.id == id,
            models.Proyecto.owner_id == current_user.id
        )
        .first()
    )
    if not alternativa:
        raise HTTPException(status_code=404, detail="Alternativa no encontrada")
    
    db.delete(alternativa)
    db.commit()
    return {"message": "Alternativa eliminada correctamente"}
