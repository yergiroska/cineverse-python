from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Review(Base):
    """
    Modelo de Reviews - reseñas de películas/series con calificación.
    """
    __tablename__ = "reviews"

    # Columnas
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    media_type = Column(String(10), nullable=False)  # 'movie' o 'tv'
    tmdb_id = Column(Integer, nullable=False)  # ID de TMDB
    rating = Column(Integer, nullable=True)  # Calificación 1-5
    content = Column(Text, nullable=True)  # Contenido de la reseña (opcional)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación con User
    user = relationship("User", back_populates="reviews")

    # Constraints
    __table_args__ = (
        # Un usuario solo puede hacer una review por media
        UniqueConstraint('user_id', 'media_type', 'tmdb_id', name='unique_user_review'),
        # Rating debe estar entre 1 y 5
        CheckConstraint('rating IS NULL OR (rating >= 1 AND rating <= 5)', name='valid_rating'),
        #CheckConstraint('rating >= 1 AND rating <= 5', name='valid_rating'),
    )

    def __repr__(self):
        return f"<Review user={self.user_id} {self.media_type}:{self.tmdb_id} rating={self.rating}>"