from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.watchlist import Watchlist
from app.schemas.watchlist import WatchlistCreate, WatchlistUpdate, WatchlistResponse, WatchlistCheck
from app.routers.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[WatchlistResponse])
async def get_watchlist(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Obtener todas las entradas de watchlist del usuario autenticado.
    """
    watchlist = db.query(Watchlist).filter(Watchlist.user_id == current_user.id).all()
    return watchlist


@router.post("/", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
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

    return new_watchlist


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