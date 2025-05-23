from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_user as get_current_user_security
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/access-token")

def get_db_session() -> Session:
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Devuelve el usuario autenticado actual a partir del token JWT.
    Lanza HTTPException si el token no es válido o el usuario no existe.
    """
    # Usa la función asíncrona de seguridad, pero aquí la llamamos de forma síncrona
    import asyncio
    return asyncio.run(get_current_user_security(db=db, token=token))