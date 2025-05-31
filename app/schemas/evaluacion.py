
from pydantic import BaseModel

class EvaluacionBase(BaseModel):
    value: float


# Propiedades para crear una evaluación
class EvaluacionCreate(EvaluacionBase):
    alternativa_id: int
    criterio_id: int
    escenario_id: int


# Propiedades para actualizar una evaluación
class EvaluacionUpdate(EvaluacionBase):
    id: int | None = None


# Propiedades en la respuesta de la API
class EvaluacionInDB(EvaluacionBase):
    id: int
    alternativa_id: int
    criterio_id: int
    escenario_id: int
    
    class Config:
        orm_mode = True


# Propiedades públicas de la evaluación para la API
class Evaluacion(EvaluacionInDB):
    pass