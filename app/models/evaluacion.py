from sqlalchemy import Column, ForeignKey, Integer, Float
from sqlalchemy.orm import relationship

from app.db.base import Base


class Evaluacion(Base):
    __tablename__ = "evaluaciones"

    id = Column(Integer, primary_key=True, index=True)
    alternativa_id = Column(Integer, ForeignKey("alternativas.id"))
    criterio_id = Column(Integer, ForeignKey("criterios.id"))
    escenario_id = Column(Integer, ForeignKey("escenarios.id"))
    value = Column(Float, nullable=False)  # Valor de la evaluación
    
    # Relaciones
    alternativa = relationship("Alternativa", back_populates="evaluaciones")
    criterio = relationship("Criterio", back_populates="evaluaciones")
    escenario = relationship("Escenario", back_populates="evaluaciones")