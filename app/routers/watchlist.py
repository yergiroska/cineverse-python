from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
import json
from app.database import get_db
from app.core.redis import get_redis
from app.models.user import User
from app.models.watchlist import Watchlist
from app.schemas.watchlist import WatchlistCreate, WatchlistUpdate, WatchlistResponse, WatchlistCheck
from app.routers.auth import get_current_user
from app.services.tmdb_service import TMDBService

router = APIRouter()


@router.get("/")
async def get_watchlist(
        media_type: Optional[str] = Query(None, description="Filtrar por tipo: 'movie' o 'tv'"),
        status: Optional[str] = Query(None, description="Filtrar por estado: 'por_ver', 'viendo', 'vista'"),
        limit: int = Query(100, ge=1, le=500, description="Límite de resultados"),
        offset: int = Query(0, ge=0, description="Offset para paginación"),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Obtener todas las entradas de watchlist del usuario autenticado.
    """

    redis_client = get_redis()
    cache_key = f"watchlist:user:{current_user.id}:type:{media_type}:status:{status}:limit:{limit}:offset:{offset}"


    if redis_client:
        cached_data = redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)

    # Query base
    query = db.query(Watchlist).filter(Watchlist.user_id == current_user.id)

    # Aplicar filtro de media_type si se proporciona
    if media_type:
        query = query.filter(Watchlist.media_type == media_type)

    # Aplicar filtro de status si se proporciona
    if status:
        query = query.filter(Watchlist.status == status)

    # Obtener total antes de paginar
    total = query.count()

    # Ordenar por más reciente y aplicar paginación
    watchlist = db.query(Watchlist).filter(Watchlist.user_id == current_user.id).all()


    # Aplicar paginación y ordenamiento
    watchlist = query.order_by(Watchlist.created_at.desc()).limit(limit).offset(offset).all()

    # Enriquecer con datos de TMDB
    tmdb_service = TMDBService()
    enriched_watchlist = []

    for watch in watchlist:
        # Llamar al método correcto según el tipo de media
        if watch.media_type == "movie":
            tmdb_data = await tmdb_service.get_movie_details(watch.tmdb_id)
        else:  # tv
            tmdb_data = await tmdb_service.get_tv_details(watch.tmdb_id)

        enriched_watchlist.append({
            "id": watch.id,
            "user_id": watch.user_id,
            "tmdb_id": watch.tmdb_id,
            "media_type": watch.media_type,
            "status": watch.status,
            "name": tmdb_data.get("title") if watch.media_type == "movie" else tmdb_data.get("name"),
            "poster_path": tmdb_data.get("poster_path"),
            "created_at": watch.created_at.isoformat() if watch.created_at else None,
            "updated_at": watch.updated_at.isoformat() if watch.updated_at else None,
        })


    # GUARDAR EN CACHE (5 minutos)
    response = {
        "watchlist": enriched_watchlist,
        "total": total
    }

    # Guardar en cache por 5 minutos
    # if redis_client:
    #     await redis_client.setex(cache_key, 300, json.dumps(response))

    return response


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_watchlist(
        watchlist_data: WatchlistCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Agregar una película o serie a la watchlist.

    - **media_type**: 'movie' o 'tv'
    - **tmdb_id**: ID de TMDB
    - **status**: 'por_ver', 'viendo' o 'vista' (default: 'por_ver')
    """
    # Verificar si ya existe
    existing = db.query(Watchlist).filter(
        and_(
            Watchlist.user_id == current_user.id,
            Watchlist.media_type == watchlist_data.media_type,
            Watchlist.tmdb_id == watchlist_data.tmdb_id
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este contenido ya está en tu watchlist"
        )

    # Crear watchlist
    new_watchlist = Watchlist(
        user_id=current_user.id,
        media_type=watchlist_data.media_type,
        tmdb_id=watchlist_data.tmdb_id,
        status=watchlist_data.status
    )

    db.add(new_watchlist)
    db.commit()
    db.refresh(new_watchlist)

    redis_client = get_redis()
    if redis_client:
        pattern = f"watchlist:user:{current_user.id}:*"
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)

    # Formatear como Laravel
    return {
        "message": "Agregado a watchlist exitosamente",
        "watchlist": {
            "id": new_watchlist.id,
            "user_id": new_watchlist.user_id,
            "tmdb_id": new_watchlist.tmdb_id,
            "media_type": new_watchlist.media_type,
            "status": new_watchlist.status,
            "created_at": new_watchlist.created_at.isoformat() if new_watchlist.created_at else None,
            "updated_at": new_watchlist.updated_at.isoformat() if new_watchlist.updated_at else None,
        }
    }


@router.put("/{watchlist_id}", response_model=WatchlistResponse)
async def update_watchlist(
        watchlist_id: int,
        watchlist_data: WatchlistUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Actualizar el estado de una entrada de watchlist.

    - **status**: 'por_ver', 'viendo' o 'vista'
    """
    watchlist = db.query(Watchlist).filter(
        and_(
            Watchlist.id == watchlist_id,
            Watchlist.user_id == current_user.id
        )
    ).first()

    if not watchlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entrada de watchlist no encontrada"
        )

    # Actualizar status
    watchlist.status = watchlist_data.status

    db.commit()
    db.refresh(watchlist)

    # INVALIDAR CACHE
    redis_client = get_redis()
    if redis_client:
        pattern = f"watchlist:user:{current_user.id}:*"
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)

    return watchlist


@router.delete("/{watchlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_watchlist(
        watchlist_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Eliminar una entrada de watchlist por ID.
    """
    watchlist = db.query(Watchlist).filter(
        Watchlist.id == watchlist_id,
        Watchlist.user_id == current_user.id
    ).first()

    if not watchlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entrada de watchlist no encontrada"
        )

    db.delete(watchlist)
    db.commit()

    # INVALIDAR CACHE
    redis_client = get_redis()
    if redis_client:
        pattern = f"watchlist:user:{current_user.id}:*"
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)

    return None


@router.get("/check/{media_type}/{tmdb_id}", response_model=WatchlistCheck)
async def check_watchlist(
        media_type: str,
        tmdb_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Verificar si una película/serie está en watchlist.

    - **media_type**: 'movie' o 'tv'
    - **tmdb_id**: ID de TMDB
    """
    watchlist = db.query(Watchlist).filter(
        Watchlist.user_id == current_user.id,
        Watchlist.media_type == media_type,
        Watchlist.tmdb_id == tmdb_id
    ).first()

    if watchlist:
        return WatchlistCheck(
            in_watchlist=True,
            watchlist_id=watchlist.id,
            status=watchlist.status
        )
    else:
        return WatchlistCheck(
            in_watchlist=False,
            watchlist_id=None,
            status=None
        )