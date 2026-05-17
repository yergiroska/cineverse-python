"""
Tests para endpoints de autenticación
"""
import pytest
from fastapi import status


class TestRegister:
    """Tests para el endpoint de registro"""

    def test_register_success(self, client):
        """Test: Registro exitoso de nuevo usuario"""
        response = client.post(
            "/api/register",
            json={
                "name": "New User",
                "email": "newuser@example.com",
                "password": "securepass123"
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["name"] == "New User"

    def test_register_duplicate_email(self, client, test_user):
        """Test: No permite registrar email duplicado"""
        response = client.post(
            "/api/register",
            json={
                "name": "Another User",
                "email": "test@example.com",  # Email del test_user
                "password": "pass123"
            }
        )

        # Acepta tanto 400 como 422
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]
        # NO validamos el mensaje porque puede ser de BD o de lógica

    def test_register_invalid_email(self, client):
        """Test: Rechaza email inválido"""
        response = client.post(
            "/api/register",
            json={
                "name": "User",
                "email": "not-an-email",
                "password": "pass123"
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLogin:
    """Tests para el endpoint de login"""

    def test_login_success(self, client, test_user):
        """Test: Login exitoso con credenciales correctas"""
        response = client.post(
            "/api/login",
            json={
                "email": "banguita@example.com",
                "password": "password123"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "banguita@example.com"

    def test_login_wrong_password(self, client, test_user):
        """Test: Login falla con contraseña incorrecta"""
        response = client.post(
            "/api/login",
            json={
                "email": "test@example.com",
                "password": "wrongpassword"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrectos" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client):
        """Test: Login falla con usuario inexistente"""
        response = client.post(
            "/api/login",
            json={
                "email": "nonexistent@example.com",
                "password": "anypassword"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestProfile:
    """Tests para el endpoint de perfil"""

    def test_get_profile_authenticated(self, client, auth_headers, test_user):
        """Test: Usuario autenticado puede ver su perfil"""
        response = client.get(
            "/api/profile",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Test User"
        assert data["email"] == "test@example.com"
        assert "password" not in data  # No debe exponer la contraseña

    def test_get_profile_unauthenticated(self, client):
        """Test: Usuario sin autenticar no puede ver perfil"""
        response = client.get("/api/profile")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_profile_invalid_token(self, client):
        """Test: Token inválido rechazado"""
        response = client.get(
            "/api/profile",
            headers={"Authorization": "Bearer invalid_token_here"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestLogout:
    """Tests para el endpoint de logout"""

    def test_logout_authenticated(self, client, auth_headers):
        """Test: Usuario autenticado puede hacer logout"""
        response = client.post(
            "/api/logout",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()


class TestGetUser:
    """Tests para el endpoint /api/user"""

    def test_get_user_authenticated(self, client, auth_headers, test_user):
        """Test: Usuario autenticado puede obtener su info"""
        response = client.get(
            "/api/user",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Test User"
        assert data["email"] == "test@example.com"
        assert "password" not in data

    def test_get_user_unauthenticated(self, client):
        """Test: Usuario sin autenticar no puede obtener info"""
        response = client.get("/api/user")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdateProfile:
    """Tests para actualizar perfil"""

    def test_update_profile_name(self, client, auth_headers, test_user):
        """Test: Actualizar nombre del perfil"""
        response = client.put(
            "/api/profile",
            headers=auth_headers,
            json={"name": "Updated Name"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["email"] == "test@example.com"  # Email sin cambiar

    def test_update_profile_email(self, client, auth_headers, test_user):
        """Test: Actualizar email del perfil"""
        response = client.put(
            "/api/profile",
            headers=auth_headers,
            json={"email": "newemail@example.com"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "newemail@example.com"
        assert data["name"] == "Test User"  # Name sin cambiar

    def test_update_profile_both(self, client, auth_headers, test_user):
        """Test: Actualizar nombre y email"""
        response = client.put(
            "/api/profile",
            headers=auth_headers,
            json={
                "name": "New Name",
                "email": "totally@new.com"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "New Name"
        assert data["email"] == "totally@new.com"

    def test_update_profile_duplicate_email(self, client, auth_headers, db_session):
        """Test: No permite actualizar a email que ya existe"""
        # Crear otro usuario
        from app.models.user import User
        from app.services.auth_service import get_password_hash

        other_user = User(
            name="Other User",
            email="other@example.com",
            password=get_password_hash("pass123")
        )
        db_session.add(other_user)
        db_session.commit()

        # Intentar cambiar a email del otro usuario
        response = client.put(
            "/api/profile",
            headers=auth_headers,
            json={"email": "other@example.com"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "en uso" in response.json()["detail"].lower()

    def test_update_profile_unauthenticated(self, client):
        """Test: Sin autenticación no puede actualizar"""
        response = client.put(
            "/api/profile",
            json={"name": "Hacker"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdatePassword:
    """Tests para cambiar contraseña"""

    def test_update_password_success(self, client, auth_headers, test_user):
        """Test: Cambiar contraseña exitosamente"""
        response = client.put(
            "/api/profile/password",
            headers=auth_headers,
            json={
                "current_password": "testpass123",
                "new_password": "newsecurepass456"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        assert "actualizada" in response.json()["message"].lower()

        # Verificar que puede hacer login con nueva contraseña
        login_response = client.post(
            "/api/login",
            json={
                "email": "test@example.com",
                "password": "newsecurepass456"
            }
        )
        assert login_response.status_code == status.HTTP_200_OK

    def test_update_password_wrong_current(self, client, auth_headers, test_user):
        """Test: Falla con contraseña actual incorrecta"""
        response = client.put(
            "/api/profile/password",
            headers=auth_headers,
            json={
                "current_password": "wrongpassword",
                "new_password": "newpass123"
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "incorrecta" in response.json()["detail"].lower()

    def test_update_password_unauthenticated(self, client):
        """Test: Sin autenticación no puede cambiar contraseña"""
        response = client.put(
            "/api/profile/password",
            json={
                "current_password": "any",
                "new_password": "newpass"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestDeleteAccount:
    """Tests para eliminar cuenta"""

    def test_delete_account_success(self, client, auth_headers, test_user):
        """Test: Eliminar cuenta exitosamente"""
        response = client.delete(
            "/api/profile",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        assert "eliminada" in response.json()["message"].lower()

        # Verificar que ya no puede hacer login
        login_response = client.post(
            "/api/login",
            json={
                "email": "test@example.com",
                "password": "testpass123"
            }
        )
        assert login_response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_account_unauthenticated(self, client):
        """Test: Sin autenticación no puede eliminar cuenta"""
        response = client.delete("/api/profile")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED