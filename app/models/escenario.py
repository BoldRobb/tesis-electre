from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, Float
from sqlalchemy.orm import relationship
import datetime

from app.db.base import Base


class Escenario(Base):
    __tablename__ = "escenarios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    corte = Column(Float, nullable=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"))
    
    # Relaciones
    proyecto = relationship("Proyecto", back_populates="escenarios")
    criterios = relationship("Criterio", back_populates="escenario", cascade="all, delete-orphan")
    alternativas = relationship("Alternativa", back_populates="escenario", cascade="all, delete-orphan")
    evaluaciones = relationship("Evaluacion", back_populates="escenario", cascade="all, delete-orphan")
