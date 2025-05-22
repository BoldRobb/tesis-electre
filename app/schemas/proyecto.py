from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


# Propiedades compartidas
class ProyectoBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


# Propiedades para crear un proyecto
class ProyectoCreate(ProyectoBase):
    title: str


# Propiedades para actualizar un proyecto
class ProyectoUpdate(ProyectoBase):
    pass


# Propiedades en la respuesta de la API
class ProyectoInDB(ProyectoBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


# Propiedades públicas del proyecto para la API
class Proyecto(ProyectoInDB):
    pass