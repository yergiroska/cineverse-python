"""
Tests para endpoints públicos de TV Shows (TMDB)
"""
import pytest
from fastapi import status


class TestTVPublicEndpoints:
    """Tests para endpoints públicos de series"""

    def test_get_popular_tv(self, client):
        """Test: Obtener series populares"""
        response = client.get("/api/tv/popular")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)

    def test_get_popular_tv_with_page(self, client):
        """Test: Obtener series populares con paginación"""
        response = client.get("/api/tv/popular?page=2")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "page" in data

    def test_get_top_rated_tv(self, client):
        """Test: Obtener series mejor calificadas"""
        response = client.get("/api/tv/top-rated")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "results" in data

    def test_get_on_the_air_tv(self, client):
        """Test: Obtener series al aire"""
        response = client.get("/api/tv/on-the-air")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "results" in data

    def test_search_tv(self, client):
        """Test: Buscar series"""
        response = client.get("/api/tv/search?query=game+of+thrones")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "results" in data

    def test_search_tv_empty_query(self, client):
        """Test: Búsqueda sin query rechazada"""
        response = client.get("/api/tv/search")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_discover_tv(self, client):
        """Test: Descubrir series"""
        response = client.get("/api/tv/discover")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "results" in data

    def test_discover_tv_with_genre(self, client):
        """Test: Descubrir series por género"""
        response = client.get("/api/tv/discover?with_genres=18")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "results" in data

    def test_get_tv_genres(self, client):
        """Test: Obtener lista de géneros"""
        response = client.get("/api/tv/genres/list")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "genres" in data

    def test_get_tv_details(self, client):
        """Test: Obtener detalles de serie"""
        response = client.get("/api/tv/1399")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert data["id"] == 1399

    def test_get_tv_similar(self, client):
        """Test: Obtener series similares"""
        response = client.get("/api/tv/1399/similar")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "results" in data

    def test_get_tv_providers(self, client):
        """Test: Obtener proveedores de streaming"""
        response = client.get("/api/tv/1399/providers")

        assert response.status_code == status.HTTP_200_OK