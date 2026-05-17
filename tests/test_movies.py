"""
Tests para endpoints públicos de Movies (TMDB)
"""
import pytest
from fastapi import status


class TestMoviesPublicEndpoints:
    """Tests para endpoints públicos de películas"""

    def test_get_popular_movies(self, client):
        """Test: Obtener películas populares"""
        response = client.get("/api/movies/popular")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)

    def test_get_popular_movies_with_page(self, client):
        """Test: Obtener películas populares con paginación"""
        response = client.get("/api/movies/popular?page=2")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "page" in data

    def test_get_top_rated_movies(self, client):
        """Test: Obtener películas mejor calificadas"""
        response = client.get("/api/movies/top-rated")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "results" in data

    def test_get_upcoming_movies(self, client):
        """Test: Obtener próximos estrenos"""
        response = client.get("/api/movies/upcoming")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "results" in data

    def test_search_movies(self, client):
        """Test: Buscar películas"""
        response = client.get("/api/movies/search?query=fight+club")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "results" in data

    def test_search_movies_empty_query(self, client):
        """Test: Búsqueda sin query rechazada"""
        response = client.get("/api/movies/search")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_discover_movies(self, client):
        """Test: Descubrir películas"""
        response = client.get("/api/movies/discover")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "results" in data

    def test_discover_movies_with_genre(self, client):
        """Test: Descubrir películas por género"""
        response = client.get("/api/movies/discover?with_genres=28")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "results" in data

    def test_get_movie_genres(self, client):
        """Test: Obtener lista de géneros"""
        response = client.get("/api/movies/genres/list")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "genres" in data


    def test_get_movie_details(self, client):
        """Test: Obtener detalles de película específica"""
        # Fight Club - ID: 550
        response = client.get("/api/movies/550")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert data["id"] == 550

    def test_get_movie_similar(self, client):
        """Test: Obtener películas similares"""
        response = client.get("/api/movies/550/similar")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "results" in data

    def test_get_movie_providers(self, client):
        """Test: Obtener proveedores de streaming"""
        response = client.get("/api/movies/550/providers")

        assert response.status_code == status.HTTP_200_OK

