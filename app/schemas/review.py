from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from typing import Literal, Optional


class ReviewBase(BaseModel):
    """Schema base de review"""
    media_type: Literal["movie", "tv"] = Field(..., description="Tipo de media: movie o tv")
    tmdb_id: int = Field(..., gt=0, description="ID de TMDB")


class ReviewCreate(ReviewBase):
    """Schema para crear review"""
    rating: Optional[int] = Field(None, ge=1, le=5, description="Calificación de 1 a 5 estrellas (opcional)")
    content: Optional[str] = Field(None, max_length=5000, description="Contenido de la reseña (opcional)")

    @model_validator(mode='after')
    def check_at_least_one_field(self):
        """Validar que al menos rating o content tenga valor"""
        if self.rating is None and (self.content is None or self.content.strip() == ""):
            raise ValueError("Debes proporcionar al menos una calificación o un comentario")
        return self


class ReviewUpdate(BaseModel):
    """Schema para actualizar review"""
    rating: Optional[int] = Field(None, ge=1, le=5, description="Nueva calificación (opcional)")
    content: Optional[str] = Field(None, max_length=5000, description="Nuevo contenido (opcional)")


class ReviewResponse(ReviewBase):
    """Schema de respuesta de review"""
    id: int
    user_id: int
    rating: Optional[int]
    content: Optional[str]
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class ReviewWithUser(ReviewResponse):
    """Schema de review con información del usuario (para listados públicos)"""
    user_name: str = Field(..., description="Nombre del usuario que hizo la review")

    class Config:
        from_attributes = True