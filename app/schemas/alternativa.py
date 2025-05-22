from typing import Optional, List
from pydantic import BaseModel


# Propiedades compartidas
class AlternativaBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


# Propiedades para crear una alternativa
class AlternativaCreate(AlternativaBase):
    name: str
    escenario_id: int


# Propiedades para actualizar una alternativa
class AlternativaUpdate(AlternativaBase):
    pass


# Propiedades en la respuesta de la API
class AlternativaInDB(AlternativaBase):
    id: int
    escenario_id: int
    
    class Config:
        orm_mode = True


# Propiedades públicas de la alternativa para la API
class Alternativa(AlternativaInDB):
    pass