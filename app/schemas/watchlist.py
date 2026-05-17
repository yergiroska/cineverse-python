from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, Optional
from app.models.watchlist import WatchlistStatus


class WatchlistBase(BaseModel):
    """Schema base de watchlist"""
    media_type: Literal["movie", "tv"] = Field(..., description="Tipo de media: movie o tv")
    tmdb_id: int = Field(..., gt=0, description="ID de TMDB")


class WatchlistCreate(WatchlistBase):
    """Schema para crear watchlist"""
    status: Optional[WatchlistStatus] = Field(default=None, description="Estado inicial (opcional)")


class WatchlistUpdate(BaseModel):
    """Schema para actualizar watchlist"""
    status: WatchlistStatus = Field(..., description="Nuevo estado")


class WatchlistResponse(WatchlistBase):
    """Schema de respuesta de watchlist"""
    id: int
    user_id: int
    status: Optional[WatchlistStatus]
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
        use_enum_values = True  # Devuelve el valor del enum, no el objeto


class WatchlistCheck(BaseModel):
    """Schema para verificar si un media está en watchlist"""
    in_watchlist: bool
    watchlist_id: int | None = None
    status: WatchlistStatus | None = None