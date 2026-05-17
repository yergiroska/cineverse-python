from pydantic import BaseModel, Field, model_validator, field_validator
from datetime import datetime
from typing import Literal, Optional


class ReviewBase(BaseModel):
    """Schema base de review"""
    media_type: Literal["movie", "tv"] = Field(..., description="Tipo de media: movie o tv")
    tmdb_id: int = Field(..., gt=0, description="ID de TMDB")


class ReviewCreate(ReviewBase):
    """Schema para crear review"""
    #lo que viene desde request de la petición sea insomnia o react
    rating: Optional[int] = Field(None, ge=1, le=5, description="Calificación de 1 a 5 estrellas (opcional)")
    review: Optional[str] = Field(None, max_length=5000, description="Alias de content para compatibilidad")


    @model_validator(mode='after')
    def check_at_least_one_field(self):
        """Validar que al menos rating o content tenga valor"""
        if self.rating is None and (self.review is None or self.review.strip() == ""):
            raise ValueError("Debes proporcionar al menos una calificación o un comentario")
        return self


class ReviewUpdate(BaseModel):
    """Schema para actualizar review"""
    rating: Optional[int] = Field(None, ge=1, le=5, description="Nueva calificación (opcional)")
    review: Optional[str] = Field(None, max_length=5000, description="Nuevo contenido (opcional)")

    @field_validator('rating', 'review', mode='before')
    @classmethod
    def empty_strings_to_none(cls, v):
        """Convierte strings vacíos a None"""
        if isinstance(v, str) and not v.strip():
            return None
        return v

class ReviewResponse(ReviewBase):
    """Schema de respuesta de review"""
    # la respuesta que se el enviá a insomnia o a react
    id: int
    user_id: int
    rating: Optional[int]
    review: Optional[str] = Field(None, serialization_alias='review', validation_alias='content')
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class ReviewWithUser(ReviewResponse):
    """Schema de review con información del usuario (para listados públicos)"""
    user_name: str = Field(..., description="Nombre del usuario que hizo la review")

    class Config:
        from_attributes = True