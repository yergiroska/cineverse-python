from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, UniqueConstraint, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum


class WatchlistStatus(str, enum.Enum):
    """Estados posibles de la watchlist"""
    plan_to_watch = "plan_to_watch"
    watching = "watching"
    completed = "completed"


class Watchlist(Base):
    """
    Modelo de Watchlist - películas/series con estado de visualización.
    """
    __tablename__ = "watchlists"

    # Columnas
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    media_type = Column(String(10), nullable=False)  # 'movie' o 'tv'
    tmdb_id = Column(Integer, nullable=False)  # ID de TMDB
    status = Column(
        Enum(WatchlistStatus, native_enum=False, length=20),
        nullable=True,
        default=None
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True
    )

    # Relación con User
    user = relationship("User", back_populates="watchlists")

    # Constraint: Un usuario no puede tener el mismo media duplicado
    __table_args__ = (
        UniqueConstraint('user_id', 'media_type', 'tmdb_id', name='unique_user_watchlist'),
    )

    def __repr__(self):
        return f"<Watchlist user={self.user_id} {self.media_type}:{self.tmdb_id} status={self.status.value}>"