from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.user import User
from app.models.watchlist import Watchlist
from app.schemas.watchlist import WatchlistCreate, WatchlistUpdate, WatchlistResponse, WatchlistCheck
from app.routers.auth import get_current_user

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
    # Query base
    query = db.query(Watchlist).filter(Watchlist.user_id == current_user.id)

    # Aplicar filtros
    if media_type:
        query = query.filter(Watchlist.media_type == media_type)

    if status:
        query = query.filter(Watchlist.status == status)

    # Obtener total antes de paginar
    total = query.count()

    # Aplicar paginación y ordenamiento
    watchlist = query.order_by(Watchlist.created_at.desc()).limit(limit).offset(offset).all()

    # Formatear como Laravel
    return {
        "watchlist": [
            {
                "id": item.id,
                "user_id": item.user_id,
                "tmdb_id": item.tmdb_id,
                "media_type": item.media_type,
                "status": item.status,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None,
            }
            for item in watchlist
        ],
        "total": total
    }


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
        Watchlist.user_id == current_user.id,
        Watchlist.media_type == watchlist_data.media_type,
        Watchlist.tmdb_id == watchlist_data.tmdb_id
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
        Watchlist.id == watchlist_id,
        Watchlist.user_id == current_user.id
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