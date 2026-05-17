"""
Tests para endpoints de Favorites
"""
import pytest
from fastapi import status


class TestCreateFavorite:
    """Tests para crear favoritos"""

    def test_create_favorite_movie(self, client, auth_headers):
        """Test: Crear favorito de película"""
        response = client.post(
            "/api/favorites",
            headers=auth_headers,
            json={
                "tmdb_id": 550,  # Fight Club
                "media_type": "movie",
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["tmdb_id"] == 550
        assert data["media_type"] == "movie"
        assert "id" in data

    def test_create_favorite_tv(self, client, auth_headers):
        """Test: Crear favorito de serie"""
        response = client.post(
            "/api/favorites",
            headers=auth_headers,
            json={
                "tmdb_id": 1399,  # Game of Thrones
                "media_type": "tv",
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["media_type"] == "tv"

    def test_create_favorite_duplicate(self, client, auth_headers):
        """Test: No permite crear favorito duplicado"""
        # Crear primer favorito
        client.post(
            "/api/favorites",
            headers=auth_headers,
            json={
                "tmdb_id": 550,
                "media_type": "movie"
            }
        )

        # Intentar crear el mismo favorito
        response = client.post(
            "/api/favorites",
            headers=auth_headers,
            json={
                "tmdb_id": 550,
                "media_type": "movie"
            }
        )

        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_create_favorite_unauthenticated(self, client):
        """Test: Sin autenticación no puede crear favorito"""
        response = client.post(
            "/api/favorites",
            json={
                "tmdb_id": 550,
                "media_type": "movie",
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetFavorites:
    """Tests para listar favoritos"""

    def test_get_favorites_empty(self, client, auth_headers):
        """Test: Lista vacía cuando no hay favoritos"""
        response = client.get(
            "/api/favorites",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_favorites_with_data(self, client, auth_headers, db_session, test_user):
        """Test: Listar favoritos del usuario"""
        from app.models.favorite import Favorite

        fav1 = Favorite(
            user_id=test_user.id,
            tmdb_id=550,
            media_type="movie"
        )
        fav2 = Favorite(
            user_id=test_user.id,
            tmdb_id=1399,
            media_type="tv"
        )
        db_session.add(fav1)
        db_session.add(fav2)
        db_session.commit()

        response = client.get(
            "/api/favorites",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        tmdb_ids = [fav["tmdb_id"] for fav in data]
        assert 550 in tmdb_ids
        assert 1399 in tmdb_ids

    def test_get_favorites_unauthenticated(self, client):
        """Test: Sin autenticación no puede listar favoritos"""
        response = client.get("/api/favorites")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

class TestDeleteFavorite:
    """Tests para eliminar favoritos"""

    def test_delete_favorite_success(self, client, auth_headers, db_session, test_user):
        """Test: Eliminar favorito exitosamente"""
        from app.models.favorite import Favorite

        favorite = Favorite(
            user_id=test_user.id,
            tmdb_id=550,
            media_type="movie"
        )
        db_session.add(favorite)
        db_session.commit()
        db_session.refresh(favorite)

        response = client.delete(
            f"/api/favorites/{favorite.id}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_favorite_not_found(self, client, auth_headers):
        """Test: Eliminar favorito inexistente devuelve 404"""
        response = client.delete(
            "/api/favorites/99999",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_favorite_unauthenticated(self, client):
        """Test: Sin autenticación no puede eliminar favorito"""
        response = client.delete("/api/favorites/1")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED