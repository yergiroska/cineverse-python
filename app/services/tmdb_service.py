import httpx
from typing import Optional, Dict, Any
from app.config import settings


class TMDBService:
    """
    Servicio para interactuar con la API de The Movie Database (TMDB).
    """

    def __init__(self):
        self.api_key = settings.TMDB_API_KEY
        self.base_url = settings.TMDB_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Método interno para hacer requests a TMDB.

        Args:
            endpoint: Endpoint de la API (ej: '/movie/popular')
            params: Query parameters adicionales

        Returns:
            Respuesta JSON de TMDB
        """
        url = f"{self.base_url}{endpoint}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params, timeout=10.0)
            response.raise_for_status()
            return response.json()

    # --- MOVIES ---

    async def get_popular_movies(self, page: int = 1, language: str = "es-ES") -> Dict[str, Any]:
        """Obtener películas populares"""
        return await self._make_request("/movie/popular", {"page": page, "language": language})

    async def get_top_rated_movies(self, page: int = 1, language: str = "es-ES") -> Dict[str, Any]:
        """Obtener películas mejor valoradas"""
        return await self._make_request("/movie/top_rated", {"page": page, "language": language})

    async def get_upcoming_movies(self, page: int = 1, language: str = "es-ES") -> Dict[str, Any]:
        """Obtener películas próximas a estrenar"""
        return await self._make_request("/movie/upcoming", {"page": page, "language": language})

    async def get_movie_details(self, movie_id: int, language: str = "es-ES") -> Dict[str, Any]:
        """Obtener detalles de una película"""
        return await self._make_request(f"/movie/{movie_id}", {"language": language})

    async def get_similar_movies(self, movie_id: int, page: int = 1, language: str = "es-ES") -> Dict[str, Any]:
        """Obtener películas similares"""
        return await self._make_request(f"/movie/{movie_id}/similar", {"page": page, "language": language})

    async def search_movies(self, query: str, page: int = 1, language: str = "es-ES") -> Dict[str, Any]:
        """Buscar películas"""
        return await self._make_request("/search/movie", {"query": query, "page": page, "language": language})

    # --- TV SHOWS ---

    async def get_popular_tv(self, page: int = 1, language: str = "es-ES") -> Dict[str, Any]:
        """Obtener series populares"""
        return await self._make_request("/tv/popular", {"page": page, "language": language})

    async def get_top_rated_tv(self, page: int = 1, language: str = "es-ES") -> Dict[str, Any]:
        """Obtener series mejor valoradas"""
        return await self._make_request("/tv/top_rated", {"page": page, "language": language})

    async def get_on_the_air_tv(self, page: int = 1, language: str = "es-ES") -> Dict[str, Any]:
        """Obtener series al aire"""
        return await self._make_request("/tv/on_the_air", {"page": page, "language": language})

    async def get_tv_details(self, tv_id: int, language: str = "es-ES") -> Dict[str, Any]:
        """Obtener detalles de una serie"""
        return await self._make_request(f"/tv/{tv_id}", {"language": language})

    async def get_similar_tv(self, tv_id: int, page: int = 1, language: str = "es-ES") -> Dict[str, Any]:
        """Obtener series similares"""
        return await self._make_request(f"/tv/{tv_id}/similar", {"page": page, "language": language})

    async def search_tv(self, query: str, page: int = 1, language: str = "es-ES") -> Dict[str, Any]:
        """Buscar series"""
        return await self._make_request("/search/tv", {"query": query, "page": page, "language": language})

    # --- GENRES ---

    async def get_movie_genres(self, language: str = "es-ES") -> Dict[str, Any]:
        """Obtener lista de géneros de películas"""
        return await self._make_request("/genre/movie/list", {"language": language})

    async def get_tv_genres(self, language: str = "es-ES") -> Dict[str, Any]:
        """Obtener lista de géneros de series"""
        return await self._make_request("/genre/tv/list", {"language": language})

    # --- PROVIDERS ---

    async def get_movie_providers(self, movie_id: int) -> Dict[str, Any]:
        """Obtener proveedores de streaming de una película"""
        return await self._make_request(f"/movie/{movie_id}/watch/providers")

    async def get_tv_providers(self, tv_id: int) -> Dict[str, Any]:
        """Obtener proveedores de streaming de una serie"""
        return await self._make_request(f"/tv/{tv_id}/watch/providers")

    # --- DISCOVER ---

    async def discover_movies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Descubrir películas con filtros personalizados"""
        return await self._make_request("/discover/movie", params)

    async def discover_tv(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Descubrir series con filtros personalizados"""
        return await self._make_request("/discover/tv", params)


# Instancia global del servicio
tmdb_service = TMDBService()