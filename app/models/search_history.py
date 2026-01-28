from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import relationship
from app.database import Base


class SearchHistory(Base):
    """
    Modelo de Historial de Búsquedas - registro de búsquedas del usuario.
    """
    __tablename__ = "search_histories"

    # Columnas
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    query = Column(String(255), nullable=False)  # Texto de búsqueda

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación con User
    user = relationship("User", back_populates="search_histories")

    # Índice para búsquedas rápidas por usuario y fecha
    __table_args__ = (
        Index('idx_user_created', 'user_id', 'created_at'),
    )

    def __repr__(self):
        return f"<SearchHistory user={self.user_id} query='{self.query}'>"