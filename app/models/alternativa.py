from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Alternativa(Base):
    __tablename__ = "alternativas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    description = Column(Text, nullable=True)
    escenario_id = Column(Integer, ForeignKey("escenarios.id"))
    
    # Relaciones
    escenario = relationship("Escenario", back_populates="alternativas")
    evaluaciones = relationship("Evaluacion", back_populates="alternativa", cascade="all, delete-orphan")
