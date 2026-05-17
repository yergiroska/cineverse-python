"""
Tests para endpoints de Search History
"""
import pytest
from fastapi import status


class TestCreateSearchHistory:
    """Tests para crear historial de búsqueda"""

    def test_create_search_history_success(self, client, auth_headers):
        """Test: Guardar búsqueda en historial"""
        response = client.post(
            "/api/search/history",
            headers=auth_headers,
            json={
                "query": "fight club"
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["query"] == "fight club"
        assert "id" in data
        assert "created_at" in data

    def test_create_search_history_empty_query(self, client, auth_headers):
        """Test: Query vacío rechazado"""
        response = client.post(
            "/api/search/history",
            headers=auth_headers,
            json={
                "query": ""
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_search_history_multiple(self, client, auth_headers):
        """Test: Permite múltiples búsquedas del mismo término"""
        # Primera búsqueda
        response1 = client.post(
            "/api/search/history",
            headers=auth_headers,
            json={"query": "inception"}
        )

        # Segunda búsqueda del mismo término (debería permitirse)
        response2 = client.post(
            "/api/search/history",
            headers=auth_headers,
            json={"query": "inception"}
        )

        assert response1.status_code == status.HTTP_201_CREATED
        assert response2.status_code == status.HTTP_201_CREATED

    def test_create_search_history_unauthenticated(self, client):
        """Test: Sin autenticación no puede guardar historial"""
        response = client.post(
            "/api/search/history",
            json={
                "query": "test"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetSearchHistory:
    """Tests para listar historial de búsqueda"""

    def test_get_search_history_empty(self, client, auth_headers):
        """Test: Lista vacía cuando no hay historial"""
        response = client.get(
            "/api/search/history",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_search_history_with_data(self, client, auth_headers, db_session, test_user):
        """Test: Listar historial del usuario"""
        from app.models.search_history import SearchHistory

        search1 = SearchHistory(
            user_id=test_user.id,
            query="fight club"
        )
        search2 = SearchHistory(
            user_id=test_user.id,
            query="inception"
        )
        search3 = SearchHistory(
            user_id=test_user.id,
            query="interstellar"
        )
        db_session.add_all([search1, search2, search3])
        db_session.commit()

        response = client.get(
            "/api/search/history",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
        queries = [item["query"] for item in data]
        assert "fight club" in queries
        assert "inception" in queries

    def test_get_search_history_ordered_by_recent(self, client, auth_headers):
        """Test: Historial ordenado por más reciente primero"""
        # Crear búsquedas en orden
        client.post("/api/search/history", headers=auth_headers, json={"query": "old search"})
        client.post("/api/search/history", headers=auth_headers, json={"query": "new search"})

        response = client.get(
            "/api/search/history",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # El más reciente debería estar primero
        assert data[0]["query"] == "new search"
        assert data[1]["query"] == "old search"

    def test_get_search_history_unauthenticated(self, client):
        """Test: Sin autenticación no puede ver historial"""
        response = client.get("/api/search/history")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestDeleteSearchHistory:
    """Tests para eliminar historial de búsqueda"""

    def test_delete_all_search_history_success(self, client, auth_headers, db_session, test_user):
        """Test: Eliminar todo el historial del usuario"""
        from app.models.search_history import SearchHistory

        # Crear múltiples búsquedas
        search1 = SearchHistory(user_id=test_user.id, query="search 1")
        search2 = SearchHistory(user_id=test_user.id, query="search 2")
        db_session.add_all([search1, search2])
        db_session.commit()

        response = client.delete(
            "/api/search/history",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verificar que el historial está vacío
        get_response = client.get("/api/search/history", headers=auth_headers)
        assert get_response.json() == []

    def test_delete_search_history_unauthenticated(self, client):
        """Test: Sin autenticación no puede eliminar historial"""
        response = client.delete("/api/search/history")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED