from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal


class FavoriteBase(BaseModel):
    """Schema base de favorito"""
    media_type: Literal["movie", "tv"] = Field(..., description="Tipo de media: movie o tv")
    tmdb_id: int = Field(..., gt=0, description="ID de TMDB")


class FavoriteCreate(FavoriteBase):
    """Schema para crear favorito"""
    pass


class FavoriteResponse(FavoriteBase):
    """Schema de respuesta de favorito"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class FavoriteCheck(BaseModel):
    """Schema para verificar si un media es favorito"""
    is_favorite: bool
    favorite_id: int | None = None