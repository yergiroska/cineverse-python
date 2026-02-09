from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.services.tmdb_service import tmdb_service

router = APIRouter()


@router.get("/popular")
async def get_popular_tv(
        page: int = Query(1, ge=1, le=500, description="Número de página"),
        language: str = Query("es-ES", description="Idioma de los resultados")
):
    """
    Obtener series populares de TMDB.
    """
    try:
        return await tmdb_service.get_popular_tv(page=page, language=language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener series populares: {str(e)}")


@router.get("/top-rated")
async def get_top_rated_tv(
        page: int = Query(1, ge=1, le=500, description="Número de página"),
        language: str = Query("es-ES", description="Idioma de los resultados")
):
    """
    Obtener series mejor valoradas de TMDB.
    """
    try:
        return await tmdb_service.get_top_rated_tv(page=page, language=language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener series top rated: {str(e)}")


@router.get("/on-the-air")
async def get_on_the_air_tv(
        page: int = Query(1, ge=1, le=500, description="Número de página"),
        language: str = Query("es-ES", description="Idioma de los resultados")
):
    """
    Obtener series al aire de TMDB.
    """
    try:
        return await tmdb_service.get_on_the_air_tv(page=page, language=language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener series on the air: {str(e)}")


@router.get("/search")
async def search_tv(
        query: str = Query(..., min_length=1, description="Texto de búsqueda"),
        page: int = Query(1, ge=1, le=500, description="Número de página"),
        language: str = Query("es-ES", description="Idioma de los resultados")
):
    """
    Buscar series en TMDB.
    """
    try:
        return await tmdb_service.search_tv(query=query, page=page, language=language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al buscar series: {str(e)}")


@router.get("/discover")
async def discover_tv(
        page: int = Query(1, ge=1, le=500, description="Número de página"),
        language: str = Query("es-ES", description="Idioma"),
        genre: Optional[str] = Query(None, description="ID de género"),
        sort_by: Optional[str] = Query("popularity.desc", description="Criterio de ordenamiento")
):
    """
    Descubrir series con filtros personalizados.
    """
    try:
        params = {
            "page": page,
            "language": language,
            "sort_by": sort_by
        }
        if genre:
            params["with_genres"] = genre

        return await tmdb_service.discover_tv(params=params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al descubrir series: {str(e)}")


@router.get("/genres/list")
async def get_tv_genres(
        language: str = Query("es-ES", description="Idioma de los géneros")
):
    """
    Obtener lista de géneros de series.
    """
    try:
        return await tmdb_service.get_tv_genres(language=language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener géneros: {str(e)}")


@router.get("/{tv_id}/similar")
async def get_similar_tv(
        tv_id: int,
        page: int = Query(1, ge=1, le=500, description="Número de página"),
        language: str = Query("es-ES", description="Idioma de los resultados")
):
    """
    Obtener series similares a una serie específica.
    """
    try:
        return await tmdb_service.get_similar_tv(tv_id=tv_id, page=page, language=language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener series similares: {str(e)}")


@router.get("/{tv_id}/providers")
async def get_tv_providers(tv_id: int):
    """
    Obtener proveedores de streaming de una serie.
    """
    try:
        return await tmdb_service.get_tv_providers(tv_id=tv_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener proveedores: {str(e)}")


@router.get("/{tv_id}")
async def get_tv_details(
        tv_id: int,
        language: str = Query("es-ES", description="Idioma de los resultados")
):
    """
    Obtener detalles de una serie específica.
    """
    try:
        return await tmdb_service.get_tv_details(tv_id=tv_id, language=language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener detalles de serie: {str(e)}")