from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
import json
from app.database import get_db
from app.core.redis import get_redis
from app.models.user import User
from app.models.favorite import Favorite
from app.schemas.favorite import FavoriteCreate, FavoriteResponse, FavoriteCheck
from app.routers.auth import get_current_user
from app.services.tmdb_service import TMDBService

router = APIRouter()


@router.get("/")
async def get_favorites(
        media_type: Optional[str] = Query(None, description="Filtrar por tipo"),
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Obtener todos los favoritos del usuario autenticado con filtros y paginación.

    - **media_type**: Opcional - 'movie' o 'tv' para filtrar
    - **limit**: Número máximo de resultados (default: 100, max: 500)
    - **offset**: Número de registros a saltar para paginación
    """

    # INTENTAR OBTENER DE CACHE PRIMERO
    redis_client = get_redis()
    cache_key = f"favorites:user:{current_user.id}:type:{media_type}:limit:{limit}:offset:{offset}"

    if redis_client:
        cached_data = redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)

    # Query base optimizada
    query = db.query(Favorite).filter(Favorite.user_id == current_user.id)

    # Aplicar filtro de media_type si se proporciona
    if media_type:
        query = query.filter(Favorite.media_type == media_type)

    # Obtener total antes de paginar
    total = query.count()

    # Aplicar paginación
    favorites = query.order_by(Favorite.created_at.desc()).limit(limit).offset(offset).all()

    # Enriquecer con datos de TMDB
    tmdb_service = TMDBService()
    enriched_favorites = []

    for fav in favorites:
        # Llamar al método correcto según el tipo de media
        if fav.media_type == "movie":
            tmdb_data = await tmdb_service.get_movie_details(fav.tmdb_id)
        else:  # tv
            tmdb_data = await tmdb_service.get_tv_details(fav.tmdb_id)

        enriched_favorites.append({
            "id": fav.id,
            "user_id": fav.user_id,
            "tmdb_id": fav.tmdb_id,
            "media_type": fav.media_type,
            "name": tmdb_data.get("title") if fav.media_type == "movie" else tmdb_data.get("name"),
            "poster_path": tmdb_data.get("poster_path"),
            "created_at": fav.created_at.isoformat() if fav.created_at else None,
            "updated_at": fav.updated_at.isoformat() if fav.updated_at else None,
        })

    response = {
        "favorites": enriched_favorites,
        "total": total
    }

    # Guardar en cache por 5 minutos
    # if redis_client:
    #     await redis_client.setex(cache_key, 300, json.dumps(response))

    return response


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_favorite(
        favorite_data: FavoriteCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Agregar una película o serie a favoritos.

    - **media_type**: 'movie' o 'tv'
    - **tmdb_id**: ID de TMDB
    """
    # Verificar si ya existe (usando and_ para mejor rendimiento)
    existing = db.query(Favorite).filter(
        and_(
            Favorite.user_id == current_user.id,
            Favorite.media_type == favorite_data.media_type,
            Favorite.tmdb_id == favorite_data.tmdb_id
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este contenido ya está en tus favoritos"
        )

    # Crear favorito
    new_favorite = Favorite(
        user_id=current_user.id,
        media_type=favorite_data.media_type,
        tmdb_id=favorite_data.tmdb_id
    )

    db.add(new_favorite)
    db.commit()
    db.refresh(new_favorite)

    # INVALIDAR CACHE - Esta es la línea que faltaba
    redis_client = get_redis()
    if redis_client:
        # Borrar todas las variaciones de cache (con diferentes filtros/paginación)
        pattern = f"favorites:user:{current_user.id}:*"
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)

    # Formatear como Laravel
    return {
        "message": "Agregado a favoritos exitosamente",
        "favorite": {
            "id": new_favorite.id,
            "user_id": new_favorite.user_id,
            "tmdb_id": new_favorite.tmdb_id,
            "media_type": new_favorite.media_type,
            "created_at": new_favorite.created_at.isoformat() if new_favorite.created_at else None,
            "updated_at": new_favorite.updated_at.isoformat() if new_favorite.updated_at else None,
        }
    }


@router.delete("/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_favorite(
        favorite_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Eliminar un favorito por ID.
    """

    # Usar and_ para mejor rendimiento con índices compuestos
    favorite = db.query(Favorite).filter(
        and_(
            Favorite.id == favorite_id,
            Favorite.user_id == current_user.id
        )
    ).first()

    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorito no encontrado"
        )

    db.delete(favorite)
    db.commit()

    return None


@router.get("/check/{media_type}/{tmdb_id}", response_model=FavoriteCheck)
async def check_favorite(
        media_type: str,
        tmdb_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Verificar si una película/serie está en favoritos.

    - **media_type**: 'movie' o 'tv'
    - **tmdb_id**: ID de TMDB
    """

    # Usar exists() es más eficiente que first() cuando solo necesitamos verificar existencia
    favorite = db.query(Favorite).filter(
        and_(
            Favorite.user_id == current_user.id,
            Favorite.media_type == media_type,
            Favorite.tmdb_id == tmdb_id
        )
    ).first()

    if favorite:
        return FavoriteCheck(is_favorite=True, favorite_id=favorite.id)
    else:
        return FavoriteCheck(is_favorite=False, favorite_id=None)


@router.delete("/{media_type}/{tmdb_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_favorite_by_tmdb(
        media_type: str,
        tmdb_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Eliminar un favorito por media_type y tmdb_id.
    """
    favorite = db.query(Favorite).filter(
        and_(
            Favorite.user_id == current_user.id,
            Favorite.media_type == media_type,
            Favorite.tmdb_id == tmdb_id
        )
    ).first()

    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorito no encontrado"
        )

    db.delete(favorite)
    db.commit()

    # INVALIDAR CACHE
    redis_client = get_redis()
    if redis_client:
        pattern = f"favorites:user:{current_user.id}:*"
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)

    return None
