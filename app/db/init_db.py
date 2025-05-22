from app.db.base import Base
from app.db.base import engine

# Importa todos los modelos para que se registren en Base.metadata
from app.models.user import User
from app.models.proyecto import Proyecto
from app.models.escenario import Escenario
from app.models.alternativa import Alternativa
from app.models.evaluacion import Evaluacion
from app.models.criterio import Criterio
# ...agrega aquí otros modelos si tienes...

class DBInitializer:
    @staticmethod
    def create_tables():
        Base.metadata.create_all(bind=engine)

    @staticmethod
    def drop_tables():
        Base.metadata.drop_all(bind=engine)