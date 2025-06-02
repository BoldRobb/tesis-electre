from typing import Optional, List
from pydantic import BaseModel, confloat


# Propiedades compartidas
class CriterioBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    weight: Optional[float] = 0.0
    is_benefit: Optional[bool] = True
    preference_threshold: Optional[float] = None
    indifference_threshold: Optional[float] = None
    veto_threshold: Optional[float] = None


# Propiedades para crear un criterio
class CriterioCreate(CriterioBase):
    name: str
    escenario_id: int


# Propiedades para actualizar un criterio
class CriterioUpdate(CriterioBase):
    pass


# Propiedades en la respuesta de la API
class CriterioInDB(CriterioBase):
    id: int
    escenario_id: int
    
    class Config:
        orm_mode = True


# Propiedades públicas del criterio para la API
class Criterio(CriterioInDB):
    pass