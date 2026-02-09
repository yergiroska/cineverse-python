from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.services.tmdb_service import tmdb_service

router = APIRouter()


@router.get("/popular")
async def get_popular_movies(
        page: int = Query(1, ge=1, le=500, description="Número de página"),
        language: str = Query("es-ES", description="Idioma de los resultados")
):
    """
    Obtener películas populares de TMDB.
    """
    try:
        return await tmdb_service.get_popular_movies(page=page, language=language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener películas populares: {str(e)}")


@router.get("/top-rated")
async def get_top_rated_movies(
        page: int = Query(1, ge=1, le=500, description="Número de página"),
        language: str = Query("es-ES", description="Idioma de los resultados")
):
    """
    Obtener películas mejor valoradas de TMDB.
    """
    try:
        return await tmdb_service.get_top_rated_movies(page=page, language=language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener películas top rated: {str(e)}")


@router.get("/upcoming")
async def get_upcoming_movies(
        page: int = Query(1, ge=1, le=500, description="Número de página"),
        language: str = Query("es-ES", description="Idioma de los resultados")
):
    """
    Obtener películas próximas a estrenar de TMDB.
    """
    try:
        return await tmdb_service.get_upcoming_movies(page=page, language=language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener películas upcoming: {str(e)}")


@router.get("/search")
async def search_movies(
        query: str = Query(..., min_length=1, description="Texto de búsqueda"),
        page: int = Query(1, ge=1, le=500, description="Número de página"),
        language: str = Query("es-ES", description="Idioma de los resultados")
):
    """
    Buscar películas en TMDB.
    """
    try:
        return await tmdb_service.search_movies(query=query, page=page, language=language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al buscar películas: {str(e)}")


@router.get("/discover")
async def discover_movies(
        page: int = Query(1, ge=1, le=500, description="Número de página"),
        language: str = Query("es-ES", description="Idioma"),
        genre: Optional[str] = Query(None, description="ID de género"),
        sort_by: Optional[str] = Query("popularity.desc", description="Criterio de ordenamiento")
):
    """
    Descubrir películas con filtros personalizados.
    """
    try:
        params = {
            "page": page,
            "language": language,
            "sort_by": sort_by
        }
        if genre:
            params["with_genres"] = genre

        return await tmdb_service.discover_movies(params=params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al descubrir películas: {str(e)}")


@router.get("/genres/list")
async def get_movie_genres(
        language: str = Query("es-ES", description="Idioma de los géneros")
):
    """
    Obtener lista de géneros de películas.
    """
    try:
        return await tmdb_service.get_movie_genres(language=language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener géneros: {str(e)}")


@router.get("/{movie_id}/similar")
async def get_similar_movies(
        movie_id: int,
        page: int = Query(1, ge=1, le=500, description="Número de página"),
        language: str = Query("es-ES", description="Idioma de los resultados")
):
    """
    Obtener películas similares a una película específica.
    """
    try:
        return await tmdb_service.get_similar_movies(movie_id=movie_id, page=page, language=language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener películas similares: {str(e)}")


@router.get("/{movie_id}/providers")
async def get_movie_providers(movie_id: int):
    """
    Obtener proveedores de streaming de una película.
    """
    try:
        return await tmdb_service.get_movie_providers(movie_id=movie_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener proveedores: {str(e)}")


@router.get("/{movie_id}")
async def get_movie_details(
        movie_id: int,
        language: str = Query("es-ES", description="Idioma de los resultados")
):
    """
    Obtener detalles de una película específica.
    """
    try:
        return await tmdb_service.get_movie_details(movie_id=movie_id, language=language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener detalles de película: {str(e)}")