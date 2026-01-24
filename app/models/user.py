from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base


class User(Base):
    """
    Modelo de Usuario para autenticación y gestión de cuenta.
    """
    __tablename__ = "users"

    # Columnas
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)  # Hash bcrypt

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User {self.email}>"