from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """Schema base de usuario"""
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=255)


class UserCreate(UserBase):
    """Schema para crear usuario (incluye password)"""
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    """Schema para login"""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema de respuesta (sin password)"""
    id: int
    #created_at: datetime
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Permite convertir desde modelo SQLAlchemy


class UserUpdate(BaseModel):
    """Schema para actualizar perfil"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None


class PasswordUpdate(BaseModel):
    """Schema para cambiar contraseña"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class Token(BaseModel):
    """Schema de respuesta con token JWT"""
    token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Datos almacenados en el token JWT"""
    email: Optional[str] = None