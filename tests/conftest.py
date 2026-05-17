import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.services.auth_service import get_password_hash
from app.config import settings

# Base de datos de testing en PostgreSQL
# Reemplaza el nombre de la BD en la URL existente
TEST_DATABASE_URL = "postgresql://postgres:123456@localhost:5432/cineverse_test"
PROD_DATABASE_URL = "postgresql://postgres:123456@localhost:5432/cineverse_python"

engine = create_engine(PROD_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    """Crea una sesión de BD limpia para cada test con transacción"""
   # connection = engine.connect()
   # transaction = connection.begin()
   # session = TestingSessionLocal(bind=connection)
    session = TestingSessionLocal()

    yield session

    session.close()
   # transaction.rollback()
   # connection.close()


@pytest.fixture
def client(db_session):
    """Cliente de prueba con BD de testing"""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Obtiene el usuario real existente"""
    user = db_session.query(User).filter_by(email="yergiroska77@gmail.com").first()

    if not user:
        raise Exception("El usuario yergiroska77@gmail.com no existe en la BD")

    return user

# def test_user(db_session):
#     """Crea un usuario de prueba"""
#     user = User(
#         name="Yergiroska",
#         email="yergiroska77@gmail.com",
#         password=get_password_hash("12345678")
#     )
#     db_session.add(user)
#     db_session.commit()
#     db_session.refresh(user)
#     return user


@pytest.fixture
def auth_token(client, test_user):
    """Obtiene token de autenticación"""
    response = client.post(
        "/api/login",
        json={
            "email": "yergiroska77@gmail.com",
            "password": "12345678"
        }
    )
    return response.json()["token"]


@pytest.fixture
def auth_headers(auth_token):
    """Headers con token de autenticación"""
    return {"Authorization": f"Bearer {auth_token}"}