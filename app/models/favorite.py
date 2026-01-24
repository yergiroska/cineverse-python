from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Favorite(Base):
    """
    Modelo de Favoritos - películas/series marcadas como favoritas por el usuario.
    """
    __tablename__ = "favorites"

    # Columnas
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    media_type = Column(String(10), nullable=False)  # 'movie' o 'tv'
    tmdb_id = Column(Integer, nullable=False)  # ID de TMDB

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación con User
    user = relationship("User", back_populates="favorites")

    # Constraint: Un usuario no puede tener el mismo media duplicado
    __table_args__ = (
        UniqueConstraint('user_id', 'media_type', 'tmdb_id', name='unique_user_favorite'),
    )

    def __repr__(self):
        return f"<Favorite user={self.user_id} {self.media_type}:{self.tmdb_id}>"