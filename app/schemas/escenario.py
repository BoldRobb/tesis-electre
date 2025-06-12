from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


# Propiedades compartidas
class EscenarioBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


# Propiedades para crear un escenario
class EscenarioCreate(EscenarioBase):
    name: str
    proyecto_id: int


# Propiedades para actualizar un escenario
class EscenarioUpdate(EscenarioBase):
    corte: Optional[float] = None
    pass


# Propiedades en la respuesta de la API
class EscenarioInDB(EscenarioBase):
    id: int
    proyecto_id: int
    created_at: datetime
    updated_at: datetime
    corte: Optional[float] = None
    
    class Config:
        orm_mode = True


# Propiedades públicas del escenario para la API
class Escenario(EscenarioInDB):
    pass