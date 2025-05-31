from typing import List, Optional
from pydantic import BaseModel, Field

class ElectreIIIRequest(BaseModel):
    alternativas_matriz: List[List[float]] = Field(..., description="Matriz de alternativas (lista de listas)")
    criterios_nombres: List[str] = Field(..., description="Nombres de los criterios")
    pesos: List[float] = Field(..., description="Pesos de cada criterio")
    preferencia: List[float] = Field(..., description="Umbrales de preferencia")
    indiferencia: List[float] = Field(..., description="Umbrales de indiferencia")
    veto: List[float] = Field(..., description="Umbrales de veto")
    direccion: List[int] = Field(..., description="Dirección de cada criterio (1=beneficio, 0=costo)")
    lambda_corte: float = Field(0.50, description="Valor de corte lambda")
    nombres_alternativas: Optional[List[str]] = Field(None, description="Nombres de las alternativas (opcional)")