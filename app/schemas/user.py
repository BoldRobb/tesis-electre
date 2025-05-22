from typing import Optional
from pydantic import BaseModel, EmailStr


# Propiedades compartidas
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    is_active: Optional[bool] = True



# Propiedades para crear el usuario
class UserCreate(UserBase):
    email: EmailStr
    name: str
    password: str


# Propiedades para actualizar el usuario
class UserUpdate(UserBase):
    password: Optional[str] = None
    name: Optional[str] = None

# Propiedades en la respuesta de la API
class UserInDB(UserBase):
    id: Optional[int] = None
    
    class Config:
        orm_mode = True


# Propiedades públicas del usuario para la API
class User(UserInDB):
    pass