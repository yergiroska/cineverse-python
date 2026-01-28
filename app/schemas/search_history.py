from pydantic import BaseModel, Field
from datetime import datetime


class SearchHistoryBase(BaseModel):
    """Schema base de search history"""
    query: str = Field(..., min_length=1, max_length=255, description="Texto de búsqueda")


class SearchHistoryCreate(SearchHistoryBase):
    """Schema para crear entrada de historial"""
    pass


class SearchHistoryResponse(SearchHistoryBase):
    """Schema de respuesta de historial"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True