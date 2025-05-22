from sqlalchemy import Column, ForeignKey, Integer, String, Float, Boolean, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Criterio(Base):
    __tablename__ = "criterios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    description = Column(Text, nullable=True)
    weight = Column(Float, default=1.0)  # Peso del criterio
    is_benefit = Column(Boolean, default=True)  # True si es beneficio, False si es costo
    escenario_id = Column(Integer, ForeignKey("escenarios.id"))
    
    # Parámetros del método ELECTRE III (opcionales)
    preference_threshold = Column(Float, nullable=True)  # Umbral de preferencia
    indifference_threshold = Column(Float, nullable=True)  # Umbral de indiferencia
    veto_threshold = Column(Float, nullable=True)  # Umbral de veto
    
    # Relaciones
    escenario = relationship("Escenario", back_populates="criterios")
    evaluaciones = relationship("Evaluacion", back_populates="criterio", cascade="all, delete-orphan")
